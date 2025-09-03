from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Start initialization
app = Flask(__name__)
session_key = 'dy6pPcQ8fnAS3Sgk'

#########################
#                       #
#       SETTINGS        #
#                       #
#########################

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
app.secret_key = session_key

# Клас юзера для бази даних
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
with app.app_context():
    db.create_all()

##########################
#                        #
#       FUNCTIONS        #
#                        #
##########################

# Внесення юзернейма в сессію
def add_session_username(username):
    session["username"] = username

# Внесення нового юзеру в бд, перевірка чи вже є такий 
def add_user(username, password):
    if User.query.filter_by(username=username).first():
        return False # такий юзер вже є
    
    new_user = User(username=username, password=password, )
    db.session.add(new_user)
    db.session.commit()
    add_session_username(username)
    print(f"New User - {username} : {password}")

    return True

# Перевірка чи є юзер з таким логіном та паролем
def check_user(username, password): 
    user = User.query.filter_by(username=username).first()
    result = False
    if user is not None and user.password == password:
        result = True
        add_session_username(username)
    return result

###############################
#                             #
#       MAIN FUNCTIONS        #
#                             #
###############################

@app.route('/')
def home():
    ip = request.remote_addr #ip
    browser = request.headers.get("User-Agent")
    ref = request.referrer
    time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    print(session.get("username"))
    
    if "username" not in session:
        return render_template("home.html", signed_in=False)
    else:
        return render_template("home.html", signed_in=True, username=session["username"])

@app.route('/profile')
def profile():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("profile.html", username=session["username"])

@app.route('/about')
def about():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("about.html", username=session["username"])

@app.route('/register', methods=['GET', 'POST', 'HOME'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        check_password = request.form['check-password']

        if check_password!=password:
            return render_template("register.html", first_try=False,check_password=True)
        else:
            res = add_user(username=username, password=password)
            if res:
                return redirect(url_for("profile", username=username))
            else: 
                return render_template('register.html', first_try=False,check_password=False)
    
    return render_template("register.html", first_try=True)

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if check_user(username=username, password=password):
            return redirect(url_for("profile"))
        else:
            return render_template("login.html", first_try=False)
        
    return render_template("login.html", first_try=True)

@app.route('/logout')
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))

####################
#                  #
#       RUN        #
#                  #
####################

if __name__ == "__main__":
    app.run(debug=True, port='5000', host='0.0.0.0')
