from backend.database import db

class StagingResponse(db.Model):
    __tablename__ = "StagingResponse"
    Id = db.Column(db.Integer, primary_key=True)
    AgentId = db.Column(db.Integer, db.ForeignKey('Agent.Id'), nullable=False)
    StagingMessageId = db.Column(db.Integer, db.ForeignKey('StagingMessageId.Id'), nullable=False)
    IV = db.Column(db.String)
    HMAC = db.Column(db.String)
    Message = db.Column(db.String)
    Sent = db.Column(db.Boolean)

    def __repr__(self):
        return '<StagingResponse: %s>' % str(self.Id)
