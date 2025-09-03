import flask, json, os
import easywebdav


# Start initialization
app = flask.Flask(__name__)

app.secret_key = "super-secret-key"  # потрібен для flash-повідомлень

ADMIN_PASSWORD = "toporkov+rust=<3"  
MEMES_FILE = "memes.json"
# Конфігурація WebDAV для Proton Drive
webdav = easywebdav.connect(
    host='webdav.proton.me',
    username=os.environ.get("PROTON_USER"),
    password=os.environ.get("PROTON_PASS"),
    protocol='https'
)

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

        # Завантаження на Proton Drive через WebDAV
        remote_path = f"/memes/{file.filename}"  # шлях у Proton Drive
        file.save(file.filename)  # тимчасово зберігаємо локально
        webdav.upload(file.filename, remote_path)
        os.remove(file.filename)  # видаляємо локальний файл

        # Формування публічного URL (в залежності від налаштувань Proton Drive)
        url = f"https://drive.proton.me/remote.php/webdav/memes/{file.filename}"

        # Додаємо новий мем у JSON
        memes = load_memes()
        memes.append({
            "title": title,
            "filename": url,
            "tags": [t.strip().lower() for t in tags if t.strip()]
        })
        save_memes(memes)

        flask.flash("✅ Мем успішно додано!")
        return flask.redirect(flask.url_for("home"))

    return flask.render_template("admin.html")


if __name__ == "__main__":
    app.run(debug=True)