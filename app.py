from flask import Flask, render_template
from flask_login import LoginManager

from accounts.models import User
from accounts.views import accounts_bp
from database import db
from url.views import url_bp
from util import cache, limiter, mail

app = Flask(__name__)
app.config.from_object("config")

cache.init_app(app)
limiter.init_app(app)
db.init_app(app)
mail.init_app(app)

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
