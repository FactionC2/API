import bcrypt
import secrets
from datetime import datetime
from backend.database import db


class ApiKey(db.Model):
    __tablename__ = "ApiKey"
    Id = db.Column(db.Integer, primary_key=True)
    UserId = db.Column(db.Integer, db.ForeignKey('User.Id'))
    OwnerId = db.Column(db.Integer)
    TransportId = db.Column(db.Integer, db.ForeignKey('Transport.Id'))
    Name = db.Column(db.String, unique=True)
    Type = db.Column(db.String)
    Key = db.Column(db.LargeBinary)
    Created = db.Column(db.DateTime)
    LastUsed = db.Column(db.DateTime)
    Enabled = db.Column(db.Boolean)
    Visible = db.Column(db.Boolean)

    def __repr__(self):
        return '<ApiKey: %s>' % str(self.Id)


