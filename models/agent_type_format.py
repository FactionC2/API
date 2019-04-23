from backend.database import db


class AgentTypeFormat(db.Model):
    __tablename__ = "AgentTypeFormat"
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String)
    AgentTypeId = db.Column(db.Integer, db.ForeignKey('AgentType.Id'), nullable=False)
    Payloads = db.relationship('Payload', backref='AgentTypeFormat', lazy=True)

    def __repr__(self):
        if self.Name:
            return '<AgentTypeFormat: %s>' % self.Name
        else:
            return '<AgentTypeFormat: %s>' % str(self.Id)



