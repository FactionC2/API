from backend.database import db


class AgentTypeArchitecture(db.Model):
    __tablename__ = "AgentTypeArchitecture"
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String)
    AgentTypeId = db.Column(db.Integer, db.ForeignKey('AgentType.Id'), nullable=False)
    Payloads = db.relationship('Payload', backref='AgentTypeArchitecture', lazy=True)

    def __repr__(self):
        if self.Name:
            return '<AgentTypeArchitecture: %s>' % self.Name
        else:
            return '<AgentTypeArchitecture: %s>' % str(self.Id)



