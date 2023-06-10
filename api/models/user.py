from ..utils import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer(), primary_key = True)
    username = db.Column(db.String(50), nullable= False, unique= True)
    email = db.Column(db.String(50), nullable= False, unique= True)
    password_hash = db.Column(db.Text(), nullable = False)
    urls = db.relationship('Url', backref='user', lazy=True)

    def __repr__(self) -> str:
        return f"<User {self.username}>"
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

