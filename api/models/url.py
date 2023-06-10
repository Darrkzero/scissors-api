from ..utils import db
from datetime import datetime

class Url(db.Model):
    __tablename__ = "urls"
    id = db.Column(db.Integer(), primary_key = True)
    long_url = db.Column(db.String(), nullable= False, unique= True)
    short_url = db.Column(db.String(), nullable= False, unique= True)
    clicks = db.Column(db.Integer(), nullable = False, default=0)
    title = db.Column(db.String(64) , nullable=True  )
    url_code = db.Column(db.String(64) , nullable=True  )
    date_created = db.Column(db.DateTime(), default=datetime.utcnow)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable = False)

    def __repr__(self) -> str:
        return f"<User {self.title}>"
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
