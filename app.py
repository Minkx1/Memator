import flask, json

# Start initialization
app = flask.Flask(__name__)

# dictionaries for initialization meme imgs in system
def load_memes():
    with open("memes.json", "r", encoding="utf-8") as f:
        return json.load(f)

memes = load_memes()

@app.route('/', methods=["GET", "POST"])
def home():
    query = flask.request.args.get("q", "").lower()
    if query:
        filtered = [m for m in memes if any(query in tag for tag in m["tags"])]
    else:
        filtered = memes
    return flask.render_template("home.html", memes=filtered, query=query)


if __name__ == "__main__":
    app.run(debug=True, port=1488)
