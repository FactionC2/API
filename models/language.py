from backend.database import db


class Language(db.Model):
    __tablename__ = "Language"
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String)
