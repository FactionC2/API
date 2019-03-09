from backend.database import db

class AgentTaskMessage(db.Model):
    __tablename__ = "AgentTaskMessage"
    Id = db.Column(db.Integer, primary_key=True)
    AgentId = db.Column(db.Integer, db.ForeignKey('Agent.Id'))
    AgentTaskId = db.Column(db.Integer, db.ForeignKey('AgentTask.Id'))
    IV = db.Column(db.String)
    HMAC = db.Column(db.String)
    Message = db.Column(db.String)
    Sent = db.Column(db.Boolean)
    Created = db.Column(db.DateTime)

    def __repr__(self):
        return '<TaskMessage: %s>' % str(self.Id)
