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

# Set the secret key for the app to some random bytes.
app.secret_key = b'8f59232c2ea24323a5e56d80f8ffd0af8c91621d927fc16a934c601d8d617416'

# creating path for the downloadable files
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'files')

# Retrieve password from the environment variable
db_password = os.getenv('DB_PASSWORD')

# SQLAlchemy configurations
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{db_password}@localhost/users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database object
db = SQLAlchemy(app)

# create login manager object
login_manager = LoginManager()

# configure app for login
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create table in the database
class User(db.Model, UserMixin):
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
        # Hashing and salting the user password
        hash_salted_password = generate_password_hash(
                password=request.form['password'],
                method='pbkdf2:sha256',
                salt_length=8,
                )
        
        # Create instance of User
        user = User(
            email = request.form['email'],
            password = hash_salted_password,
            name = request.form['name'],
        )

        # Add user to the database
        db.session.add(user)
        db.session.commit()

        # Login the registered user
        login_user(user)

        # Redirect the user after registration and login
        return redirect(url_for('secrets', name=user.name))
    
    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        login_password = request.form.get('password')

        # Retrieve data associated with the user email
        user = User.query.filter_by(email=email).first()
        # Check for hashed_password match
        password_match = check_password_hash(user.password, login_password)
        if user and password_match:
            login_user(user)
            return redirect(url_for('secrets', name=user.name))
        
    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    name = request.args.get('name')
    return render_template("secrets.html", name=name)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/download')
@login_required
def download():
    return send_from_directory(app.config['UPLOAD_FOLDER'], 'cheat_sheet.pdf')


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
