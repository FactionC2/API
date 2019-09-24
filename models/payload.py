from backend.database import db
from models.staging_message import StagingMessage


class Payload(db.Model):
    __tablename__ = "Payload"
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String, unique=True)
    Description = db.Column(db.String)
    Key = db.Column(db.String)

    Built = db.Column(db.Boolean)
    BuildToken = db.Column(db.String)
    Filename = db.Column(db.String)

    AgentTypeId = db.Column(db.Integer, db.ForeignKey('AgentType.Id'), nullable=False)
    AgentTypeArchitectureId = db.Column(db.Integer, db.ForeignKey('AgentTypeArchitecture.Id'), nullable=False)
    AgentTypeConfigurationId = db.Column(db.Integer, db.ForeignKey('AgentTypeConfiguration.Id'), nullable=False)
    AgentTypeOperatingSystemId = db.Column(db.Integer, db.ForeignKey('AgentTypeOperatingSystem.Id'), nullable=False)
    AgentTypeVersionId = db.Column(db.Integer, db.ForeignKey('AgentTypeVersion.Id'), nullable=False)
    AgentTypeFormatId = db.Column(db.Integer, db.ForeignKey('AgentTypeFormat.Id'), nullable=False)
    AgentTransportTypeId = db.Column(db.Integer, db.ForeignKey('AgentTransportType.Id'), nullable=False)
    TransportId = db.Column(db.Integer, db.ForeignKey('Transport.Id'), nullable=False)

    BeaconInterval = db.Column(db.Integer)
    Jitter = db.Column(db.Float)
    Created = db.Column(db.DateTime)
    LastDownloaded = db.Column(db.DateTime)
    ExpirationDate = db.Column(db.DateTime)
    Enabled = db.Column(db.Boolean)

    Agents = db.relationship('Agent', backref='Payload', lazy=True)
    StagingMessages = db.relationship("StagingMessage", backref='StagingConfig', lazy=True)
    Visible = db.Column(db.Boolean)

    def __repr__(self):
            return '<Payload: %s>' % str(self.Id)
