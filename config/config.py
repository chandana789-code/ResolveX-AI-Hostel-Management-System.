import os

class Config:
    SECRET_KEY = "hostel_secret_key"

    SQLALCHEMY_DATABASE_URI = "sqlite:///hostel.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = "uploads"
