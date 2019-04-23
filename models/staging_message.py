from backend.database import db

class StagingMessage(db.Model):
    __tablename__ = "StagingMessage"
    Id = db.Column(db.Integer, primary_key=True)
    AgentName = db.Column(db.String)
    SourceIp = db.Column(db.String)
    PayloadName = db.Column(db.String)
    PayloadId = db.Column(db.Integer, db.ForeignKey('Payload.Id'), nullable=False)
    TransportId = db.Column(db.Integer, db.ForeignKey('Transport.Id'), nullable=False)
    StagingId = db.Column(db.String)
    IV = db.Column(db.String)
    HMAC = db.Column(db.String)
    Message = db.Column(db.String)
    Received = db.Column(db.DateTime)

    def __repr__(self):
        return '<StagingMessage: %s>' % str(self.Id)
