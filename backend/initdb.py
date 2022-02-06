from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from hashlib import md5

def init(path, key) -> SQLAlchemy:
    app = Flask("__main__")
    app.config["SQLALCHEMY_DATABASE_URI"] = path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = md5(key.encode('utf8')).hexdigest()
    db = SQLAlchemy(app)
    return db, app
