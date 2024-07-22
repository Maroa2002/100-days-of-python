#!/usr/bin/env python3
""" authentication """

from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import os

# Create flask app
app = Flask(__name__)

# CSRF_Token secret key
app.config['SECRET_KEY'] = 'secret-key-goes-here'

# creating path for the downloadable files
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'files')

# Retrieve password from the environment variable
db_password = os.getenv('DB_PASSWORD')
print(db_password)

# SQLAlchemy configurations
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{db_password}@localhost/users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database object
db = SQLAlchemy(app)

# Create table in the database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

    def __repr__(self):
        return f"<User: {self.name}>"



@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        user = User(
            email = email,
            password = password,
            name = name,
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('secrets', name=user.name))
    return render_template("register.html")


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/secrets')
def secrets():
    name = request.args.get('name')
    return render_template("secrets.html", name=name)


@app.route('/logout')
def logout():
    pass


@app.route('/download')
def download():
    return send_from_directory(app.config['UPLOAD_FOLDER'], 'cheat_sheet.pdf')


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
