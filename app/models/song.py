from app import db

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist = db.Column(db.String(50), nullable=False)
    releases = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    lyrics = db.Column(db.Text, nullable=False)