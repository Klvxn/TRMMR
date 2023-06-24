import os
from pathlib import Path
from flask import Flask
from flask_login import LoginManager
from links.views import links_bp
from accounts.views import accounts_bp
from accounts.models import User
from database import db
from util import cache, limiter


app = Flask(__name__)

BASE_PATH = Path(__file__).resolve().parent
DATABASE_PATH = os.path.join(BASE_PATH, "database")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_PATH}/TRMMRDB"
app.config["SECRET_KEY"] = "safe-space"
app.config["CACHE_TYPE"] = "simple"
app.config["RATELIMIT_HEADERS_ENABLED"] = True
app.config["ENV"] = "development"

cache.init_app(app)
limiter.init_app(app)
db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(links_bp)
app.register_blueprint(accounts_bp)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "accounts.log_in"


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


if __name__ == '__main__':
    app.run()
