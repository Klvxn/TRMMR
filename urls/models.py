from datetime import datetime

from user_agents import parse

from database import db


class ShortenedURL(db.Model):

    __tablename__ = "shortened_urls"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    # title = db.Column(db.String, nullable=True)
    original_url = db.Column(db.String, nullable=False)
    short_url = db.Column(db.String, nullable=False, unique=True)
    unique_id = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_visited = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    clicks = db.relationship("Click", backref="url_clicks", lazy=True)

    def __init__(self, **kwargs):
        self.unique_id = kwargs["short_url"].split("/")[-1]
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def is_password_protected(self):
        return self.password is not None

    def get_total_clicks(self):
        return len(self.clicks)

    @classmethod
    def get_user_recent_urls(cls, user_id):
        return cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc())


class Click(db.Model):

    __tablename__ = "clicks"

    id = db.Column(db.Integer, primary_key=True)
    device = db.Column(db.String(100))
    browser = db.Column(db.String)
    clicked_at = db.Column(db.Date, default=datetime.now)
    link_id = db.Column(db.Integer, db.ForeignKey("shortened_urls.id"))

    def __repr__(self):
        return f"Click for ShortenedURL: {self.link_id}"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def record_click(self, url, request):
        url.last_visited = datetime.now()
        ua_string = request.headers.get("User-Agent")
        user_agent = parse(ua_string)
        self.device = user_agent.os.family
        self.browser = user_agent.browser.family
        self.clicked_at = datetime.now()
        self.link_id = url.id
        self.save()
        return
