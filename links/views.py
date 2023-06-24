import io

import qrcode
from flask import Blueprint, render_template, request, redirect, make_response, send_file
from flask_login import current_user, login_required

from database import db
from util import cache, limiter, generate_short_url, encode_qrcode_image
from .models import Link

links_bp = Blueprint("links", __name__)


@links_bp.route("/", methods=["GET", "POST"])
@limiter.limit("10/minute")
def shorten_url():
    context = {"current_user": current_user}

    if request.method == "POST":
        long_url = request.form.get("urlInput")

        url_exist = Link.query.filter_by(org_url=long_url).first()
        if url_exist:
            short_url = url_exist.short_url
        else:
            short_url = generate_short_url()

        user_id = current_user.id if current_user.is_authenticated else 0
        link = Link(org_url=long_url, short_url=short_url, user_id=user_id)
        db.session.add(link)
        db.session.commit()

        context["short_url"] = short_url

    return render_template("home.html", **context)


@links_bp.route("/<short_url>", methods=["GET"])
@limiter.limit("10/minute")
def redirect_to_org_url(short_url):
    url = Link.query.filter_by(short_url=short_url).first_or_404()
    return redirect(url.org_url)


@links_bp.route("/generate-qrcode", methods=["GET", "POST"])
@login_required
def generate_qrcode():
    if request.method == "POST":
        url_form = request.form.get("url")
        url_arg = request.args.get("url")

        if url_arg:
            encoded_image = encode_qrcode_image(url_arg)
            return make_response(f"""
                <img src='data:image/png;base64,{encoded_image}' alt='' height=330 width=330>
            """)

        if url_form:
            encoded_image = encode_qrcode_image(url_form)
            return make_response(f"""
                <p><img src='data:image/png;base64,{encoded_image}' alt='' height=330 width=330></p>
                <form action="" method="post">
                    <button>Download</button>
                </form>
            """)

        # Download QR code image
        qr_code = qrcode.make(url_form)
        image_stream = io.BytesIO()
        qr_code.save(image_stream, "PNG")
        image_stream.seek(0)
        return send_file(image_stream, download_name="qr_code.png", as_attachment=True)

    return render_template("qrcode.html")


@links_bp.route("/history", methods=["GET", "POST"])
@cache.cached(timeout=50)
@login_required
def user_history():
    context = {"links": current_user.links}

    if request.method == "POST":
        for link in current_user.links:
            db.session.delete(link)
            db.session.commit()
        return redirect("/history")

    return render_template("history.html", **context)
