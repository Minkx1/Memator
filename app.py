import flask, json, os, hashlib

# --- Config ---
MEMES_FILE = "memes.json"
UPLOAD_FOLDER = "static/memes"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD_HASH") or "4a58953f9be61a1b54ff79b686507c308df4de956ab7b46e63d2d373ade79d8e"
SECRET_KEY = "super-secret-key"

# --- Flask ---
app = flask.Flask(__name__)
app.secret_key = SECRET_KEY# for flash msg-s

# --- Helpers ---
def encode(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_memes():
    with open("memes.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_memes(memes):
    with open(MEMES_FILE, "w", encoding="utf-8") as f:
        json.dump(memes, f, ensure_ascii=False, indent=4)

# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def home():
    memes = load_memes()
    query = ""

    if flask.request.method == "POST": query = flask.request.form.get("search", "").lower()
    else: query = flask.request.args.get("search", "").lower()

    if query:
        memes = [
            m for m in memes
            if m.get("visible", True) and (query in m["title"].lower() or any(query in tag for tag in m["tags"]))
        ]
    else:
        memes = [m for m in memes if m.get("visible", True)]

    return flask.render_template("home.html", memes=memes, query=query)

@app.route("/admin")
def admin():
    return flask.render_template("admin_hub.html")

@app.route("/admin/add", methods=["GET", "POST"])
def admin_add():
    if flask.request.method == "POST":
        password = flask.request.form.get("password")
        title = flask.request.form.get("title")
        tags = flask.request.form.get("tags", "").split(",")
        file = flask.request.files.get("file")

        if encode(password) != ADMIN_PASSWORD:
            flask.flash("❌ Невірний пароль!")
            return flask.redirect(flask.url_for("admin"))

        if not file or file.filename == "":
            flask.flash("❌ Не вибрано файл!")
            return flask.redirect(flask.url_for("admin"))

        # Збереження картинки
        filename = file.filename
        file.save(os.path.join(UPLOAD_FOLDER, filename))

        # Додаємо новий мем у JSON
        memes = load_memes()
        memes.append({
            "title": title,
            "filename": filename,
            "tags": [t.strip().lower() for t in tags if t.strip()],
            "visible": True
        })
        save_memes(memes)

        flask.flash("✅ Мем успішно додано!")
        return flask.redirect(flask.url_for("home"))

    return flask.render_template("admin_add.html")

@app.route("/admin/manage", methods=["GET", "POST"])
def admin_manage():
    memes = load_memes()

    if flask.request.method == "POST":
        # Отримуємо всі видимі меми
        visible_ids = flask.request.form.getlist("visible")  # список filename мемів, які залишаються видимими
        for m in memes:
            m["visible"] = m["filename"] in visible_ids
        save_memes(memes)
        flask.flash("✅ Налаштування мемів оновлено!")
        return flask.redirect(flask.url_for("admin_manage"))

    return flask.render_template("admin_manage.html", memes=memes)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)