from flask import Blueprint, flash, redirect, render_template, request, make_response
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

from database import db
from .models import User
from .forms import LoginForm, UserForm

accounts_bp = Blueprint("accounts", __name__)


@accounts_bp.route("/create-new-account/", methods=["GET", "POST"])
def sign_up():
    form = UserForm()

    if form.validate_on_submit():
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email_address = form.email_address.data
        user = User(first_name, last_name, email_address, password)
        user.save_to_db()
        login_user(user)
        flash("Registration was successful", "success")
        return redirect("/log-in/")

    return render_template("signup.html", form=form)


@accounts_bp.route("/log-in/", methods=["GET", "POST"])
def log_in():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email_address.data
        password = form.password.data
        user = User.get_user_by_email(email)

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_url = request.args.get("next")
            if next_url:
                return redirect(next_url)

            flash("You are logged in successfully", "success")
            return redirect("/")

        else:
            flash("Invalid email or password", "error")

    return render_template("login.html", form=form)


@accounts_bp.route("/log-out", methods=["POST"])
@login_required
def log_out():
    logout_user()
    flash("You are now logged out", "warning")
    return redirect("/")


@accounts_bp.route("/account-settings/", methods=["GET", "POST", "DELETE"])
@login_required
def account_settings():
    form = UserForm()

    if request.method == "POST":
        current_user.email_address = form.email_address.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        db.session.commit()
        response = make_response()
        response.headers["HX-Location"] = "/account-settings"
        flash("Update was successful", "success")
        return response

    if request.method == "DELETE":
        if current_user.links:
            for link in current_user.links:
                db.session.delete(link)
                db.session.commit()

        db.session.delete(current_user)
        db.session.commit()
        response = make_response()
        response.headers["HX-Redirect"] = "/"
        return response

    return render_template("settings.html", form=form)
