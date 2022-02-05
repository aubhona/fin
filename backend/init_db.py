from flask import Flask
from flask_sqlalchemy import SQLAlchemy


def initdb(path) -> SQLAlchemy:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)
    return db
