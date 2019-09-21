from backend.database import db


class Module(db.Model):
    __tablename__ = "Module"
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String)
    Description = db.Column(db.String)
    BuildCommand = db.Column(db.String)
    BuildLocation = db.Column(db.String)
    LanguageId = db.Column(db.Integer, db.ForeignKey('Language.Id'))
