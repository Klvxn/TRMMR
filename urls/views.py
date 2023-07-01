import base64, io
from datetime import datetime

import qrcode
from flask import Blueprint, flash, make_response, render_template, request, redirect, send_file
from flask_login import current_user, login_required
from matplotlib import pyplot as plt
from werkzeug.security import check_password_hash, generate_password_hash

from database import db
from util import cache, limiter, generate_short_url, encode_qrcode_image
from .models import ShortenedURL, Click

url_bp = Blueprint("url", __name__)


@url_bp.route("/", methods=["GET", "POST"])
@limiter.limit("20/minute")
def shorten_url():
    cached = cache.get("short_link")
    context = {"current_user": current_user, "cached": cached}
    
    if current_user.is_authenticated:
        last_shortened_url = ShortenedURL.query.filter_by(user_id=current_user.id).order_by(ShortenedURL.created_at.desc()).first()
        context["last_shortened_url"] = last_shortened_url
            

    if request.method == "POST":
        long_url = request.form.get("long_url")
        custom_url = request.form.get("custom_half")
        short_url = None

        if current_user.is_authenticated:
            user_id = current_user.id
            url_exist = ShortenedURL.query.filter_by(org_url=long_url, user_id=user_id).first()
            
            if url_exist:
                short_url = url_exist.short_url

                if custom_url:
                    _url = custom_url.replace(" ", "-")
                    short_url = request.host_url + _url
                    url_exist.short_url = short_url
                    url_exist.unique_id = _url
                    db.session.commit()
                
            else:
                short_url = generate_short_url(custom_url=custom_url) if custom_url else generate_short_url()
                new_url = ShortenedURL(org_url=long_url, short_url=short_url, user_id=user_id)

                db.session.add(new_url)
                db.session.commit()
        
        else:
            short_link = short_url = generate_short_url(custom_url=custom_url) if custom_url else generate_short_url()
            cache.set("short_link", short_link, timeout=60)
        
        context["short_url"] = short_url

    return render_template("home.html", **context)


@url_bp.route("/<unique_id>/set/url-password", methods=["POST"])
def set_url_password(unique_id):
    short_url = request.host_url + unique_id
    url = ShortenedURL.query.filter_by(short_url=short_url).first()

    new_password = request.form.get("url_password")
    url.password = generate_password_hash(new_password)
    db.session.commit()
    flash("URL is now secured", "success")
    return redirect("/")


@url_bp.route("/<unique_id>", methods=["GET"])
@limiter.limit("20/minute")
def redirect_to_org_url(unique_id):
    short_url = request.host_url + unique_id
    url = ShortenedURL.query.filter_by(short_url=short_url, unique_id=unique_id).first_or_404()

    if url.is_password_protected:
        flash("This URL is password protected. Enter password to gain access.")
        return render_template("password.html", unique_id=url.unique_id)

    Click.update_click_record(url, request)
    return redirect(url.org_url)


@url_bp.route("/<unique_id>/authenticate", methods=["GET", "POST"])
def check_url_password(unique_id):
    short_url = request.host_url + unique_id
    url = ShortenedURL.query.filter_by(short_url=short_url).first_or_404()

    if request.method == "POST":
        password = request.form.get("password")

        if password and check_password_hash(url.password, password):
            Click.update_click_record(url, request)
            return redirect(url.org_url)

        flash("The password you entered is invalid", "error")
    return render_template("password.html", unique_id=url.unique_id)


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
@cache.cached(timeout=30)
@login_required
def user_history():
    user_urls = ShortenedURL.query.filter_by(user_id=current_user.id).order_by(ShortenedURL.created_at.desc()).all()

    # Clear URL history
    if request.method == "POST":
        
        for link in current_user.links:
            db.session.delete(link)
            db.session.commit()
            
        return redirect("/history")

    context = {"urls": user_urls}
    return render_template("history.html", **context)


@url_bp.route("/analytics/<unique_id>", methods=["GET"])
@login_required
def url_analytics(unique_id):
    short_url = request.host_url + unique_id
    url = ShortenedURL.query.filter_by(short_url=short_url).first_or_404()
    context = {"url": url, "clicks": url.clicks}

    if url.get_total_clicks():

        # Pie chart for most used platforms(OS)
        devices = [click.device for click in url.clicks]
        device_count = {}
        
        for device in devices:
            if device in device_count:
                device_count[device] += 1
            else: 
                device_count[device] = 1

        labels = device_count.keys()
        sizes = device_count.values()
        
        plt.figure()
        plt.pie(sizes, autopct='%1.1f%%', startangle=90)
        plt.title("Most Used Platforms", loc="center", fontsize=20)
        plt.subplots_adjust(bottom=0)
        plt.legend(labels, title="Platforms", loc="center left", bbox_to_anchor=(0.9, 0.5),
                   handlelength=1, ncol=1, borderpad=1, handletextpad=1)

        buffer1 = io.BytesIO()
        plt.savefig(buffer1, format="png")
        buffer1.seek(0)
        graph1 = base64.b64encode(buffer1.getvalue()).decode()

        # Bar chart for clicks per day
        target_dates = set()
        for click in url.clicks:
            target_dates.add(click.clicked_at)

        clicks = Click.query.filter_by(link_id=url.id)
        click_count = {}

        for date in target_dates:
            click_day = clicks.filter_by(clicked_at=date).all()
            try:
                click_count[date] += len(click_day)
            except KeyError:
                click_count[date] = len(click_day)

        dates = [str(date) for date in click_count.keys()]
        values = [value for value in click_count.values()]

        plt.figure()
        plt.bar(x=dates, height=values, width=0.2, color="lime")
        plt.xlabel("Date", fontsize=12)
        plt.xticks(rotation=30)
        plt.ylabel("Clicks", fontsize=12)
        plt.title("Clicks/Day Count", fontsize=20, pad=40)
        plt.subplots_adjust(bottom=0.2, top=0.8)

        buffer2 = io.BytesIO()
        plt.savefig(buffer2, format="png")
        buffer2.seek(0)
        graph2 = base64.b64encode(buffer2.getvalue()).decode()
        
        # Create a bar chart for browsers
        browsers = [click.browser for click in url.clicks]
        browser_counts = {}
        
        for browser in browsers:
            if browser in browser_counts:
                browser_counts[browser] += 1
            else:
                browser_counts[browser] = 1

        most_used_browser = max(browser_counts.items(), key=lambda x: x[1])
        browser_labels = browser_counts.keys()
        counts = browser_counts.values()

        plt.figure()
        plt.bar(browser_labels, counts, width=0.3, color="purple")
        plt.xlabel("Browsers")
        plt.ylabel("Clicks")
        plt.title("Browser Distribution", fontsize=20, pad=40)
        plt.subplots_adjust(bottom=0.2, top=0.8)
        plt.xticks(rotation=45)
        
        buffer3 = io.BytesIO()
        plt.savefig(buffer3, format="png")
        buffer3.seek(0)
        graph3 = base64.b64encode(buffer3.getvalue()).decode()
        

        # Get the day with most clicks
        zipped = zip(dates, values)
        max_clicks_day = list(max(dict(zipped).items(), key=lambda x: x[1]))
        new_format = datetime.strptime(max_clicks_day[0], "%Y-%m-%d")
        max_clicks_day[0] = new_format.strftime("%b %d, %Y")

        context.update({
            "platform_chart": graph1,
            "click_chart": graph2,
            "browser_chart": graph3,
            "click_count": click_count,
            "max_clicks_day": max_clicks_day,
            "most_used_browser": most_used_browser
        })

    return render_template("analytics.html", **context)
