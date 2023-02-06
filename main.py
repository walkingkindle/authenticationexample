import werkzeug.security
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'Ub(2zX1%9y5AdG'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"



##CREATE TABLE IN DB
class User(UserMixin, db.Model):
    with app.app_context():
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(100), unique=True)
        password = db.Column(db.String(100))
        name = db.Column(db.String(1000))
    #Line below only required once, when creating DB.
        # db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register',methods=["GET","POST"])
def register():
    if request.method == "POST":
        user_mail = db.session.query(User).filter_by(email=request.form.get("email")).first()
        if user_mail:
            flash("This user already exist. You can log in!")
            return redirect(url_for("login"))
        else:
            hashed_passwords = generate_password_hash(request.form.get("password"),method="pbkdf2:sha256",salt_length=8)
            new_user = User(
                    email=request.form.get("email"),
                    name=request.form.get("name"),
                    password=hashed_passwords
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("secrets",logged_in=True))
    return render_template("register.html")


@app.route('/login',methods=["POST","GET"])
def login():
    if request.method == "POST":
        entered_email = request.form.get("email")
        entered_password = request.form.get("password")
        user = db.session.query(User).filter_by(email=entered_email).first()
        if user:
            if check_password_hash(pwhash=user.password,password=entered_password):
                login_user(user)
                return redirect(url_for("secrets",logged_in=True))
            else:
                flash("Invalid password")
                return render_template("login.html")
        else:
            flash("This email does not exist.")
            return render_template("login.html")

    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    print(current_user.name)
    return render_template("secrets.html",name=current_user.name,logged_in=True)


@app.route('/logout',methods=["GET","POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route('/download/<path:filename>')
def download(filename):
    return send_from_directory('static/files/',"cheat_sheet.pdf")



if __name__ == "__main__":
    app.run(debug=True)
