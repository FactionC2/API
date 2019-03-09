from backend.database import db

# Even though the API doesn't handle tasks (Core does that), we need to define this model
# so we can have an agent object thats inline with the DB
class AgentTask(db.Model):
    __tablename__ = "AgentTask"
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String)
    AgentId = db.Column(db.Integer, db.ForeignKey('Agent.Id'), nullable=False)
    ConsoleMessageId = db.Column(db.Integer, db.ForeignKey('ConsoleMessage.Id'), nullable=True)
    AgentTaskUpdates = db.relationship('AgentTaskUpdate', backref='AgentTask', lazy=True)
    Action = db.Column(db.String)
    Command = db.Column(db.String)
    Created = db.Column(db.DateTime)


    def __repr__(self):
        return '<Task: %s>' % str(self.Id)


