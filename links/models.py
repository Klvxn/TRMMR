from database import db


class Link(db.Model):

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    url = db.Column(db.String, nullable=False)
    shortened_url = db.Column(db.String, nullable=False)
    total_clicks = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


