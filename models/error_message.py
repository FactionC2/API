from backend.database import db


class ErrorMessage(db.Model):
    __tablename__ = "ErrorMessage"
    Id = db.Column(db.Integer, primary_key=True)
    Source = db.Column(db.String)
    Message = db.Column(db.String)
    Details = db.Column(db.String)
    Timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return '<ErrorMessage: {0} - {1}>'.format(self.Source, self.Message)


