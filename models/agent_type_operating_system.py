from backend.database import db


class AgentTypeOperatingSystem(db.Model):
    __tablename__ = "AgentTypeOperatingSystem"
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String)
    AgentTypeId = db.Column(db.Integer, db.ForeignKey('AgentType.Id'), nullable=False)
    Payloads = db.relationship('Payload', backref='AgentTypeOperatingSystem', lazy=True)

    def __repr__(self):
        if self.Name:
            return '<AgentTypeOperatingSystem: %s>' % self.Name
        else:
            return '<AgentTypeOperatingSystem: %s>' % str(self.Id)



