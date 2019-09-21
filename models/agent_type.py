from backend.database import db
from models.agent_type_format import AgentTypeFormat
from models.agent_type_architecture import AgentTypeArchitecture
from models.agent_type_configuration import AgentTypeConfiguration
from models.agent_type_operating_system import AgentTypeOperatingSystem
from models.agent_type_version import AgentTypeVersion
from models.agent_transport_type import AgentTransportType


class AgentType(db.Model):
    __tablename__ = "AgentType"
    Id = db.Column(db.Integer, primary_key=True)
    Agents = db.relationship('Agent', backref='AgentType', lazy=True)
    Payloads = db.relationship('Payload', backref='AgentType', lazy=True)
    AgentTransportTypes = db.relationship('AgentTransportType', backref='AgentType', lazy=True)
    AgentTypeArchitectures = db.relationship('AgentTypeArchitecture', backref='AgentType', lazy=True)
    AgentTypeConfigurations = db.relationship('AgentTypeConfiguration', backref='AgentType', lazy=True)
    AgentTypeFormats = db.relationship('AgentTypeFormat', backref='AgentType', lazy=True)
    AgentTypeOperatingSystems = db.relationship('AgentTypeOperatingSystem', backref='AgentType', lazy=True)
    AgentTypeVersions = db.relationship('AgentTypeVersion', backref='AgentType', lazy=True)
    Payloads = db.relationship('Payload', backref='AgentType', lazy=True)
    Commands = db.relationship('Command', backref='AgentType', lazy=True)
    Name = db.Column(db.String)
    Guid = db.Column(db.String)

    def __repr__(self):
        return '<AgentType: %s>' % str(self.Id)
