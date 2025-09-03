import flask, json, os

# Start initialization
app = flask.Flask(__name__)

app.secret_key = "super-secret-key"  # потрібен для flash-повідомлень

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")  # зміни на свій пароль
MEMES_FILE = "memes.json"
UPLOAD_FOLDER = "static/memes/"

# dictionaries for initialization meme imgs in system
def load_memes():
    with open("memes.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_memes(memes):
    with open(MEMES_FILE, "w", encoding="utf-8") as f:
        json.dump(memes, f, ensure_ascii=False, indent=4)

@app.route('/', methods=["GET", "POST"])
def home():
    memes = load_memes() # gets memes data from json
    query = flask.request.args.get("ask", "").lower() # gets info from search label
    
    filtered = []

    if query:
        for m in memes:
            for tag in m['tags']:
                if query in tag:
                    filtered.append(m) # adds to $filtered$ memes that in tags have query
                    break
    else:
        filtered = memes

    return flask.render_template("home.html", memes=filtered, query=query) # renders template

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if flask.request.method == "POST":
        password = flask.request.form.get("password")
        title = flask.request.form.get("title")
        tags = flask.request.form.get("tags", "").split(",")
        file = flask.request.files.get("file")

        if password != ADMIN_PASSWORD:
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
            "tags": [t.strip().lower() for t in tags if t.strip()]
        })
        save_memes(memes)

        flask.flash("✅ Мем успішно додано!")
        return flask.redirect(flask.url_for("home"))

    return flask.render_template("admin.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render передає порт у змінній PORT
    app.run(host="0.0.0.0", port=port)