from datetime import datetime
from database import db


class Link(db.Model):

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    # title = db.Column(db.String, nullable=True)
    org_url = db.Column(db.String, nullable=False)
    short_url = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    last_visited = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    clicks = db.relationship("Click", backref="url_clicks",  lazy=True)

    def get_total_clicks(self):
        return len(self.clicks)


class Click(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    device = db.Column(db.String(100))
    clicked_at = db.Column(db.Date, default=datetime.now)
    link_id = db.Column(db.Integer, db.ForeignKey("link.id"))

    def __repr__(self):
        return f"Click for Link: {self.link_id}"

    def save(self):
        db.session.add(self)
        db.session.commit()
