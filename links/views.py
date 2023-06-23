import qrcode

from flask import Blueprint, render_template, request, redirect, make_response
from flask_login import current_user, login_required
from pyshorteners.shorteners import clckru

from database import db
from .models import Link

links_bp = Blueprint("links", __name__)


@links_bp.route("/", methods=["GET", "POST"])
def shorten_url():
    context = {"current_user": current_user}

    if request.method == "POST":
        url = request.form.get("urlInput")
        shortened_url = clckru.Shortener().short(url)
        context["shortened_url"] = shortened_url

        if current_user.is_authenticated:
            link = Link(url=url, shortened_url=shortened_url, total_clicks=3, user_id=current_user.id)
            db.session.add(link)
            db.session.commit()

    return render_template("home.html", **context)


@links_bp.route("/generate-qrcode", methods=["GET", "POST"])
@login_required
def generate_qrcode():
    if request.method == "POST":
        url_form = request.form.get("url")
        url_arg = request.args.get("url")

        if url_arg:
            print("yes")
            qrcode.make(url_arg).save("static/code.png")
            return make_response("<img src='static/code.png' alt=''>")

        if url_form:
            qr = qrcode.make(url_form)
            short = clckru.Shortener().short(url_form).strip("https://clck.ru")
            image_url = f"static/{short}_image.png"
            qr.save(image_url)
            return make_response(f"<img src='{image_url}' alt='' height=330 width=330>")

    return render_template("qrcode.html")


@links_bp.route("/history", methods=["GET", "POST"])
@login_required
def user_history():
    context = {"links": current_user.links}

    if request.method == "POST":
        for link in current_user.links:
            db.session.delete(link)
            db.session.commit()
        return redirect("/history")

    return render_template("history.html", **context)
