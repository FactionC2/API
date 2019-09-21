from backend.database import db
from models.command_parameter import CommandParameter


class Command(db.Model):
    __tablename__ = "Command"
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String)
    Description = db.Column(db.String)
    Help = db.Column(db.String)
    MitreReference = db.Column(db.String)
    OpsecSafe = db.Column(db.Boolean)
    ModuleId = db.Column(db.Integer, db.ForeignKey('Module.Id'))
    AgentTypeId = db.Column(db.Integer, db.ForeignKey('AgentType.Id'))
    Parameters = db.relationship('CommandParameter', backref='Command', lazy=True)
