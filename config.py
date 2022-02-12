import os
from hashlib import md5

SECRET_KEY = md5("PredProffessonal".encode('utf8')).hexdigest()
DEBUG = True
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'site.db')
