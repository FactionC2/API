from backend.database import db


class CommandParameter(db.Model):
    __tablename__ = "CommandParameter"
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String)
    Help = db.Column(db.String)
    Required = db.Column(db.Boolean)
    Position = db.Column(db.Integer)
    Values = db.Column(db.String)
    CommandId = db.Column(db.Integer, db.ForeignKey('Command.Id'))
