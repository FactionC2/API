from backend.database import db

class AgentCheckin(db.Model):
    __tablename__ = "AgentCheckin"
    Id = db.Column(db.Integer, primary_key=True)
    AgentId = db.Column(db.Integer, db.ForeignKey('Agent.Id'))
    IV = db.Column(db.String)
    HMAC = db.Column(db.String)
    Message = db.Column(db.String)
    Received = db.Column(db.DateTime)

    def __repr__(self):
        return '<AgentCheckin: %s>' % str(self.Id)


