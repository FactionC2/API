from backend.database import db
from models.agent_type_format import AgentTypeFormat
from models.agent_transport_type import AgentTransportType

class AgentType(db.Model):
    __tablename__ = "AgentType"
    Id = db.Column(db.Integer, primary_key=True)
    Agents = db.relationship('Agent', backref='AgentType', lazy=True)
    Payloads = db.relationship('Payload', backref='AgentType', lazy=True)
    AgentTypeFormats = db.relationship('AgentTypeFormat', backref='AgentType', lazy=True)
    AgentTransportTypes = db.relationship('AgentTransportType', backref='AgentType', lazy=True)
    Name = db.Column(db.String)
    Guid = db.Column(db.String)

    def __repr__(self):
        return '<AgentType: %s>' % str(self.Id)