from backend.database import db

class AgentTransportType(db.Model):
    __tablename__ = "AgentTransportType"
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String)
    TransportTypeGuid = db.Column(db.String)
    BuildCommand = db.Column(db.String)
    BuildLocation = db.Column(db.String)
    AgentTypeId = db.Column(db.Integer, db.ForeignKey('AgentType.Id'), nullable=False)
    Payloads = db.relationship('Payload', backref='AgentTransportType', lazy=True)

    def __repr__(self):
        return '<AgentType: %s>' % str(self.Id)