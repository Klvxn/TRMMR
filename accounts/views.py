import secrets

from flask import Blueprint, flash, make_response, redirect, render_template, request, session, url_for
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from werkzeug.security import check_password_hash, generate_password_hash

from database import db
from util import mail
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

            flash("You are now logged in", "success")
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


@accounts_bp.route("/forgot-password/", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":
        email = request.form.get("email")
        email_exists = User.query.filter_by(email_address=email).first()
        if not email_exists:
            flash("This email is not registered in our system", "error")

        else:
            token = secrets.token_urlsafe(32)
            reset_url = request.host_url + f"recovery/reset-password?token={token}"

            session["reset_token"] = token
            session["user_email"] = email

            msg = Message(subject="Password Reset", recipients=[email], sender="trmmr@admin.io")
            msg.html = render_template("reset_password_email.html", reset_url=reset_url)
            mail.send(msg)
            flash("Reset link has been sent to your email.")

    return render_template("forgot_pwd.html")


@accounts_bp.route("/recovery/reset-password/", methods=["GET", "POST"])
def reset_password():
    saved_token = session.get("token")
    token = request.args.get("token")
    user_email = session.get("user_email")
    
    if token == saved_token:

        if request.method == "POST":
            new_pass1 = request.form.get("password1")
            new_pass2 = request.form.get("password2")

            if new_pass1 == new_pass2 and new_pass2:
                user = User.query.filter_by(email_address=user_email).first()
                user.password_hash = generate_password_hash(new_pass1)
                db.session.commit()

                flash("Password reset successful", "success")
                return redirect(url_for(".log_in"))

            else:
                flash("Passwords don't match", 'error')

    return render_template("reset_password.html")
