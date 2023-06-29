import os
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent
DATABASE_PATH = os.path.join(BASE_PATH, "database")
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}/TRMMRDB"
SECRET_KEY = "safe-space"
CACHE_TYPE = "FileSystemCache"
CACHE_THRESHOLD = 200
CACHE_DIR = os.path.join(BASE_PATH, "cache/app")
CACHE_DEFAULT_TIMEOUT = 60
RATELIMIT_HEADERS_ENABLED = True
ENV = "production"
DEBUG = False
PREFERRED_URL_SCHEME = "https"
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
MAIL_DEFAULT_SENDER = "trmmr@admin.io"
MAIL_SUPPRESS_SEND = False
MAIL_DEBUG = False
