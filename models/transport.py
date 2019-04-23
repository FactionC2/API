from backend.database import db

class Transport(db.Model):
    __tablename__ = "Transport"
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String)
    TransportType = db.Column(db.String)
    Guid = db.Column(db.String)
    Created = db.Column(db.DateTime)
    LastCheckin = db.Column(db.DateTime)
    Configuration = db.Column(db.String)
    ApiKeyId = db.Column(db.Integer, db.ForeignKey('ApiKey.Id'), nullable=False)
    Enabled = db.Column(db.Boolean)
    Visible = db.Column(db.Boolean)
    Agents = db.relationship('Agent', backref='Transport', lazy=True)
    Payloads = db.relationship('Payload', backref='Transport', lazy=True)

    def __repr__(self):
        return '<Transport: %s>' % str(self.Id)


