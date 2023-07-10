import base64, io, math
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
    context = {"current_user": current_user}
    
    if current_user.is_authenticated:
        last_shortened_url = ShortenedURL.get_user_recent_urls(current_user.id).first()
        context["last_shortened_url"] = last_shortened_url

    if request.method == "POST":
        long_url = request.form.get("long_url")
        custom_url = request.form.get("custom_half")

        if current_user.is_authenticated:
            user_id = current_user.id
            url_exist = ShortenedURL.query.filter_by(original_url=long_url, user_id=user_id).first()
            
            if url_exist:
                short_url = url_exist.short_url

                if custom_url:
                    _url = custom_url.replace(" ", "-")
                    custom_name_exist = ShortenedURL.query.filter_by(unique_id=_url).first()

                    if not custom_name_exist:
                        short_url = request.host_url + _url
                        url_exist.short_url = short_url
                        url_exist.unique_id = _url
                        db.session.commit()

                    else:
                        flash(f"A URL with custom name: {custom_url}, already exists", "error")

            else:
                short_url, error = generate_short_url(custom_url=custom_url) if custom_url else generate_short_url()

                if not error:
                    new_url = ShortenedURL(original_url=long_url, short_url=short_url, user_id=user_id)
                    db.session.add(new_url)
                    db.session.commit()

                else:
                    flash(error, "error")
        else:
            short_url, _ = generate_short_url()

        context["short_url"] = short_url

    return render_template("home.html", **context)


@url_bp.route("/set/url-password/<unique_id>", methods=["POST"])
def set_url_password(unique_id):
    new_password = request.form.get("url_password")
    short_url = request.host_url + unique_id
    url = ShortenedURL.query.filter_by(short_url=short_url).first()
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

    Click().record_click(url, request)
    return redirect(url.original_url)


@url_bp.route("/authenticate/url/<unique_id>", methods=["GET", "POST"])
def check_url_password(unique_id):
    short_url = request.host_url + unique_id
    url = ShortenedURL.query.filter_by(short_url=short_url).first_or_404()

    if request.method == "POST":
        password = request.form.get("password")

        if password and check_password_hash(url.password, password):
            Click().record_click(url, request)
            return redirect(url.original_url)

        flash("The password you entered is invalid", "error")
    return render_template("password.html", unique_id=url.unique_id)


@url_bp.route("/qrcodes/generate/", methods=["GET", "POST"])
@login_required
def generate_qrcode():
    if request.method == "POST":
        form_url = request.form.get("url")
        arg_url = request.args.get("url")

        html_resp = """
            <p><img src="data:image/png;base64,{}" alt="QR CODE" height=330 width=330></p>
            <form action="/download-qrcode?url={}" method="post">
                <button>Download</button>
            </form>
        """

        url = arg_url or form_url
        encoded_image = encode_qrcode_image(url)
        html_resp = html_resp.format(encoded_image, url)
        return make_response(html_resp)

    return render_template("qrcode.html")


@url_bp.route("/download-qrcode", methods=["GET", "POST"])
@login_required
def download_qrcode():
    url = request.args.get("url")
    qr_code = qrcode.make(url)
    image_stream = io.BytesIO()
    qr_code.save(image_stream, "PNG")
    image_stream.seek(0)
    return send_file(image_stream, download_name="qr_code.png", as_attachment=True)


@url_bp.route("/history", methods=["GET", "POST"])
@login_required
def user_history():
    page = int(request.args.get("page", 1))
    per_page = 3
    url_history = ShortenedURL.get_user_recent_urls(current_user.id).paginate(page=page, per_page=per_page)
    total_results = ShortenedURL.get_user_recent_urls(current_user.id).count()
    total_pages = math.ceil(total_results / per_page)

    # Clear URL history
    if request.method == "POST":
        
        for link in current_user.links:
            db.session.delete(link)
            db.session.commit()
            
        return redirect("/history")

    context = {"url_history": url_history, "page": page, "total_pages": total_pages}
    return render_template("history.html", **context)


@url_bp.route("/delete/url/<unique_id>", methods=["POST"])
@login_required
def delete_shortened_url(unique_id):
    url = ShortenedURL.query.filter_by(user_id=current_user.id, unique_id=unique_id).first()
    db.session.delete(url)
    db.session.commit()
    response = make_response()
    response.headers.add("HX-Refresh", "true")
    return response  


@url_bp.route("/analytics/url/<unique_id>", methods=["GET"])
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
        target_dates = [click.clicked_at for click in url.clicks]
        dates_count = {}

        for date in target_dates:
            if date in dates_count:
                dates_count[date] += 1
            else:
                dates_count[date] = 1

        date_labels = [str(date) for date in dates_count.keys()]
        values = [value for value in dates_count.values()]

        plt.figure()
        plt.bar(x=date_labels, height=values, width=0.2, color="lime")
        plt.xlabel("Date", fontsize=12)
        plt.xticks(rotation=30)
        plt.ylabel("Clicks", fontsize=12)
        plt.title("Clicks/Day Count", fontsize=20, pad=40)
        plt.subplots_adjust(bottom=0.2, top=0.8)

        buffer2 = io.BytesIO()
        plt.savefig(buffer2, format="png")
        buffer2.seek(0)
        graph2 = base64.b64encode(buffer2.getvalue()).decode()
        
        # Get the day with most clicks
        zipped = zip(date_labels, values)
        max_clicks_day = list(max(dict(zipped).items(), key=lambda x: x[1]))
        new_format = datetime.strptime(max_clicks_day[0], "%Y-%m-%d")
        max_clicks_day[0] = new_format.strftime("%b %d, %Y")
        
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

        context.update({
            "platform_chart": graph1,
            "click_chart": graph2,
            "browser_chart": graph3,
            "max_clicks_day": max_clicks_day,
            "most_used_browser": most_used_browser
        })

    return render_template("analytics.html", **context)
