#!/usr/bin/env python3
""" Books app """

from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
import os

# Create app
app = Flask(__name__)

# Retrieve the password
db_password = os.getenv('DB_PASSWORD')
if not db_password:
    raise ValueError("No DB_PASSWORD set for Flask application")


# SQLAlchemy configurations
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{db_password}@localhost/books_collection'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False, unique=True)
    author = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return "<Book {}>".format(self.title)


# home page
@app.route('/')
def home():
    return render_template('index.html')

# /add page
@app.route('/add')
def add():
    return render_template('add.html')


if __name__ == "__main__":
    # Initialize the database and create tables
    with app.app_context():
        db.create_all()
    app.run(debug=True)