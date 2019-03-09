from backend.database import db

class FactionFile(db.Model):
    __tablename__ = "FactionFile"
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String)
    Hash = db.Column(db.String)
    HashMatch = db.Column(db.Boolean)
    UserId = db.Column(db.Integer, db.ForeignKey('User.Id'))
    AgentId = db.Column(db.Integer, db.ForeignKey('Agent.Id'))
    Created = db.Column(db.DateTime)
    LastDownloaded = db.Column(db.DateTime)
    Visible = db.Column(db.Boolean)

    def __repr__(self):
        return '<FactionFile: %s>' % str(self.Id)


