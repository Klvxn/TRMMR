import os
from pathlib import Path

from flask import Flask, render_template
from flask_login import LoginManager

from accounts.models import User
from accounts.views import accounts_bp
from database import db
from url.views import url_bp
from util import cache, limiter


app = Flask(__name__)

BASE_PATH = Path(__file__).resolve().parent
DATABASE_PATH = os.path.join(BASE_PATH, "database")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_PATH}/TRMMRDB"
app.config["SECRET_KEY"] = "safe-space"
app.config["CACHE_TYPE"] = "FileSystemCache"
app.config["CACHE_THRESHOLD"] = 100
app.config["CACHE_DIR"] = os.path.join(BASE_PATH, "cache/app")
app.config["CACHE_DEFAULT_TIMEOUT"] = 60
app.config["RATELIMIT_HEADERS_ENABLED"] = True
app.config["ENV"] = "development"
app.config["DEBUG"] = True
app.config["PREFERRED_URL_SCHEME"] = "https"

cache.init_app(app)
limiter.init_app(app)
db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(url_bp)
app.register_blueprint(accounts_bp)

login_manager = LoginManager(app)
login_manager.login_view = "accounts.log_in"
login_manager.login_message_category = "error"


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


if __name__ == '__main__':
    app.run()
