import base64, io

import nanoid, qrcode
from flask import request
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail

from urls.models import ShortenedURL

cache = Cache()
limiter = Limiter(get_remote_address)
mail = Mail()


def generate_short_url(custom_url=None):
    host = request.host_url
    error = None

    if not custom_url:

        while True:
            unique_id = nanoid.generate(size=12)
            url_exist = ShortenedURL.query.filter_by(unique_id=unique_id).first()
            if not url_exist:
                break

    else:
        unique_id = custom_url.replace(" ", "-")
        custom_name_exist = ShortenedURL.query.filter_by(unique_id=unique_id).first()

        if custom_name_exist:
            error = f"A URL with custom name: {unique_id}, already exists"
            unique_id = None

    new_short_url = host + unique_id if unique_id else ""
    return new_short_url, error


def encode_qrcode_image(data):
    qr = qrcode.QRCode(version=1, box_size=20, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    qr_code = qr.make_image(fill="black", back_color="white")
    image_stream = io.BytesIO()
    qr_code.save(image_stream, "PNG")
    image_stream.seek(0)
    encoded_image = base64.b64encode(image_stream.getvalue()).decode('utf-8')
    return encoded_image
