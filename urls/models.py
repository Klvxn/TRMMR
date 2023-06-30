from datetime import datetime
from database import db


class ShortenedURL(db.Model):

    __tablename__ = "shortened_urls"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    # title = db.Column(db.String, nullable=True)
    org_url = db.Column(db.String, nullable=False)
    short_url = db.Column(db.String, nullable=False)
    unique_id = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_visited = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    clicks = db.relationship("Click", backref="url_clicks",  lazy=True)

    def __init__(self, **kwargs):
        self.unique_id = kwargs["short_url"].split("/")[-1]
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def is_password_protected(self):
        return self.password is not None

    def get_total_clicks(self):
        return len(self.clicks)


class Click(db.Model):

    __tablename__ = "clicks"

    id = db.Column(db.Integer, primary_key=True)
    device = db.Column(db.String(100))
    clicked_at = db.Column(db.Date, default=datetime.now)
    link_id = db.Column(db.Integer, db.ForeignKey("shortened_urls.id"))

    def __repr__(self):
        return f"Click for ShortenedURL: {self.link_id}"

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def update_click_record(url, request):
        url.last_visited = datetime.now()
        device = request.headers.get("Sec-Ch-Ua-Platform", "Others").strip("\"")
        clicked_at = datetime.now()
        click = Click(device=device, clicked_at=clicked_at, link_id=url.id)
        click.save()
        return
