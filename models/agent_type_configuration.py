from backend.database import db


class AgentTypeConfiguration(db.Model):
    __tablename__ = "AgentTypeConfiguration"
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String)
    AgentTypeId = db.Column(db.Integer, db.ForeignKey('AgentType.Id'), nullable=False)
    Payloads = db.relationship('Payload', backref='AgentTypeConfiguration', lazy=True)

    def __repr__(self):
        if self.Name:
            return '<AgentTypeConfiguration: %s>' % self.Name
        else:
            return '<AgentTypeConfiguration: %s>' % str(self.Id)



