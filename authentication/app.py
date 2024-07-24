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
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Set the secret key for the app
app.secret_key = os.getenv('SECRET_KEY')

# Create path to the downloadable files
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'files')

# DB password
db_password = os.getenv('DB_PASSWORD')

# SQLAlchemy configurations
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{db_password}@localhost/users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database object
db = SQLAlchemy(app)

# LoginManager object
login_manager = LoginManager()

# Configure app for login
login_manager.init_app(app)

# user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return User.query.get_or_404(int(user_id))

# User class
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
        return redirect(url_for('secrets'))
    
    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check for empty email and password fields
        if not email or not password:
            flash('Email and Password are required!', 'error')
            return redirect(url_for('login'))

        # Query for user data associated with the email
        user = User.query.filter_by(email=email).first()
        if user:
            # Check for hashed_password match
            password_match = check_password_hash(user.password, password)
            if password_match:
                login_user(user)
                flash('Successfully logged in!', 'success')
                return redirect(url_for('secrets'))
            else:
                flash('Incorrect Password!', 'error')
                return redirect(url_for('login'))
        else:
            flash('Email does not exist.Please Try Again!', 'error')
            return redirect(url_for('login'))                    
        
    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    current_user_name = current_user.name
    return render_template("secrets.html", name=current_user_name)


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
