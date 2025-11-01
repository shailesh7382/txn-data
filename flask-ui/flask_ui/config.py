import os

class BaseConfig:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///users.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AUTO_CREATE_DB = True
    JSON_SORT_KEYS = False
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

class DevConfig(BaseConfig):
    DEBUG = True

class TestConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    AUTO_CREATE_DB = True

class ProdConfig(BaseConfig):
    DEBUG = False
    AUTO_CREATE_DB = False

