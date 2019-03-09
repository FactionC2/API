from backend.database import db


class ConsoleMessage(db.Model):
    __tablename__ = "ConsoleMessage"
    Id = db.Column(db.Integer, primary_key=True)
    AgentId = db.Column(db.Integer, db.ForeignKey('Agent.Id'), nullable=False)
    AgentTaskId = db.Column(db.Integer, db.ForeignKey('AgentTask.Id'), nullable=False)
    UserId = db.Column(db.Integer, db.ForeignKey('User.Id'), nullable=False)
    Type = db.Column(db.String)
    Content = db.Column(db.String)
    Display = db.Column(db.String)
    Received = db.Column(db.DateTime)

    def __repr__(self):
        return '<ConsoleCommand: %s>' % str(self.Id)


