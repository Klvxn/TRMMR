import io
from datetime import datetime

import qrcode
from flask import Blueprint, render_template, request, redirect, make_response, send_file
from flask_login import current_user, login_required
from matplotlib import pyplot as plt

from database import db
from util import cache, limiter, generate_short_url, encode_qrcode_image
from .models import Link, Click

url_bp = Blueprint("url", __name__)


@url_bp.route("/", methods=["GET", "POST"])
@limiter.limit("20/minute")
def shorten_url():
    context = {"current_user": current_user}

    if request.method == "POST":
        long_url = request.form.get("long_url")
        # custom_url = request.form.get("custom_url")
        url_exist = Link.query.filter_by(org_url=long_url).first()
        if url_exist:
            short_url = url_exist.short_url
        else:
            short_url = generate_short_url()

        user_id = current_user.id if current_user.is_authenticated else 0
        new_url = Link(org_url=long_url, short_url=short_url, user_id=user_id)
        db.session.add(new_url)
        db.session.commit()

        context["short_url"] = short_url

    return render_template("home.html", **context)


@url_bp.route("/<unique_id>", methods=["GET"])
@limiter.limit("20/minute")
@cache.cached(timeout=60)
def redirect_to_org_url(unique_id):
    short_url = request.host_url + unique_id
    url = Link.query.filter_by(short_url=short_url).first_or_404()
    url.last_visited = datetime.now()
    device = request.headers.get("Sec-Ch-Ua-Platform").strip("\"")
    clicked_at = datetime.now()
    click = Click(device=device, clicked_at=clicked_at, link_id=url.id)
    click.save()
    return redirect(url.org_url)


@url_bp.route("/generate-qrcode", methods=["GET", "POST"])
@login_required
def generate_qrcode():
    if request.method == "POST":
        url_form = request.form.get("url")
        url_arg = request.args.get("url")

        html_resp = """
            <p><img src="data:image/png;base64,{}" alt="QR CODE" height=330 width=330></p>
            <form action="/generate-qrcode" method="post">
                <button>Download</button>
            </form>
        """

        if url_arg:
            encoded_image = encode_qrcode_image(url_arg)
            html_resp = html_resp.format(encoded_image)
            return make_response(html_resp)

        if url_form:
            encoded_image = encode_qrcode_image(url_form)
            html_resp = html_resp.format(encoded_image)
            return make_response(html_resp)

        # Download QR code image
        qr_code = qrcode.make(url_form)
        image_stream = io.BytesIO()
        qr_code.save(image_stream, "PNG")
        image_stream.seek(0)
        return send_file(image_stream, download_name="qr_code.png", as_attachment=True)

    return render_template("qrcode.html")


@url_bp.route("/history", methods=["GET", "POST"])
@cache.cached(timeout=50)
@login_required
def user_history():
    context = {"urls": current_user.links}

    # Clear URL history
    if request.method == "POST":
        for link in current_user.links:
            db.session.delete(link)
            db.session.commit()
        return redirect("/history")

    return render_template("history.html", **context)


@url_bp.route("/analytics/<unique_id>", methods=["GET"])
@login_required
def url_analytics(unique_id):
    short_url = request.host_url + unique_id
    url = Link.query.filter_by(short_url=short_url).first_or_404()

    devices = {
        "Windows": 0,
        "Mac": 0,
        "Linux": 0,
        "Android": 0,
        "iOS": 0,
        "Others": 0,
        "None": 1
    }
    for click, device in zip(url.clicks, devices.keys()):
        if click.device == device:
            devices[device] += 1

    labels = [device for device in devices.keys()]
    sizes = [value for value in devices.values()]
    fig, ax = plt.subplots()
    ax.pie(sizes, autopct='%d%%', startangle=90)
    ax.axis('equal')
    plt.legend(labels, title="Platforms", loc="center left", bbox_to_anchor=(0.84, 0.5),
               handlelength=1, ncol=1, borderpad=1, handletextpad=1)
    chart_file = 'static/images/chart.png'
    plt.savefig(chart_file)

    context = {"url": url, "clicks": url.clicks}
    return render_template("analytics.html", **context)
