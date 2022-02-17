import os
from hashlib import md5
from datetime import timedelta

SECRET_KEY = md5("CTRFin".encode("utf8")).hexdigest()
DEBUG = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "site.db")
