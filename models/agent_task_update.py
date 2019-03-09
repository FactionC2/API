from backend.database import db

class AgentTaskUpdate(db.Model):
    __tablename__ = "AgentTaskUpdate"
    Id = db.Column(db.Integer, primary_key=True)
    AgentId = db.Column(db.Integer, db.ForeignKey('Agent.Id'))
    TaskId = db.Column(db.Integer, db.ForeignKey('AgentTask.Id'))
    Message = db.Column(db.String)
    Complete = db.Column(db.Boolean)
    Success = db.Column(db.Boolean)
    Received = db.Column(db.DateTime)
    IOCs = db.relationship("IOC", backref='AgentTaskUpdate', lazy=True)

    def __repr__(self):
        return '<AgentTaskUpdate: %s>' % str(self.Id)
