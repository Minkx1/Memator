import flask, json, os, hashlib
import rapidfuzz.fuzz

# some shit for commit?

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

MEMES = load_memes() # Глобально кешуємо

# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def home():
    return flask.render_template("home.html")
@app.route("/api/get_memes", methods=["GET"])
def get_memes():
    query = flask.request.args.get("query", "").strip().lower()

    seen = set()
    result = {
        "ok": True,
        "result": []
    }

    for meme in MEMES:
        if len(query) == 0:
            if meme["filename"] not in seen:
                result["result"].append({
                    "filename": meme["filename"],
                    "title": meme["title"],
                    "url": f"/{UPLOAD_FOLDER}/{meme['filename']}",
                    "tags": meme["tags"],
                })
                seen.add(meme["filename"])
            continue

        match = False
        if rapidfuzz.fuzz.ratio(query, meme["title"]) >= 80. or query in meme["title"].lower():
            match = True

        for tag in meme["tags"]:
            if rapidfuzz.fuzz.ratio(query, tag) >= 80. or query in tag:
                match = True
                break

        if match and meme["filename"] not in seen:
            result["result"].append({
                "filename": meme["filename"],
                "title": meme["title"],
                "url": f"/{UPLOAD_FOLDER}/{meme['filename']}",
                "tags": meme["tags"],
            })
            seen.add(meme["filename"])

    return flask.jsonify(result)

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
        password = flask.request.form.get("password")

        # Перевірка пароля
        if encode(password) != ADMIN_PASSWORD:
            flask.flash("❌ Невірний пароль!")
            return flask.redirect(flask.url_for("admin_manage"))

        # Оновлюємо видимість мемів
        for m in memes:
            checkbox_name = f"visible_{m['filename']}"
            m["visible"] = checkbox_name in flask.request.form

        save_memes(memes)
        flask.flash("✅ Налаштування мемів оновлено!")
        return flask.redirect(flask.url_for("admin_manage"))

    return flask.render_template("admin_manage.html", memes=memes)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug="DEBUG" in os.environ.keys(), host="0.0.0.0", port=port)