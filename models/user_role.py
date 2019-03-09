from backend.database import db

class UserRole(db.Model):
    __tablename__ = "UserRole"
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String, nullable=False, unique=True)
    Users = db.relationship('User', backref='UserRole', lazy=True)


    def __repr__(self):
        return '<Role: %s>' % str(self.Id)


