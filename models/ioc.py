from backend.database import db

class IOC(db.Model):
    __tablename__ = "IOC"
    Id = db.Column(db.Integer, primary_key=True)
    Description = db.Column(db.String)
    Type = db.Column(db.String)
    Identifier = db.Column(db.String)
    Action = db.Column(db.String)
    Hash = db.Column(db.String)
    UserId = db.Column(db.Integer, db.ForeignKey('User.Id'))
    AgentTaskUpdateId = db.Column(db.Integer, db.ForeignKey('AgentTaskUpdate.Id'))
    Timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return '<IOC: %s>' % str(self.Id)


