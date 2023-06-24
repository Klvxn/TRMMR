import base64, io

import nanoid, qrcode
from flask import request
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

cache = Cache()
limiter = Limiter(get_remote_address)


def generate_short_url():
    host = request.host_url
    unique_id = nanoid.generate(size=12)
    new_short_url = host + unique_id
    return new_short_url


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
