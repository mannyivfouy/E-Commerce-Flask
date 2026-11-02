from datetime import timedelta
import os

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///mydb.sqlite3"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=10)
