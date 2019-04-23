from backend.database import db


class AgentTypeVersion(db.Model):
    __tablename__ = "AgentTypeVersion"
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String)
    AgentTypeId = db.Column(db.Integer, db.ForeignKey('AgentType.Id'), nullable=False)
    Payloads = db.relationship('Payload', backref='AgentTypeVersion', lazy=True)

    def __repr__(self):
        if self.Name:
            return '<AgentTypeVersion: %s>' % self.Name
        else:
            return '<AgentTypeVersion: %s>' % str(self.Id)



