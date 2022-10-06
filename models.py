from email import contentmanager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

# User model
class User(db.Model):
    """User model"""

    __tablename__ = "users";

    username = db.Column (db.String(20), primary_key = True, unique = True, nullable = False)
    password = db.Column (db.Text, nullable = False)
    email = db.Column (db.String(50), nullable = False, unique = True)
    first_name = db.Column (db.String(30), nullable = False)
    last_name = db.Column (db.String(30), nullable = False)

    feedback = db.relationship ("Feedback", backref="user", cascade ="all, delete")

    @classmethod
    def register (cls, username, password, email, first_name, last_name):
        """Register a user, hashing their password"""
        hashed = bcrypt.generate_password_hash (password)
        print (hashed)
        hashed_utf8 = hashed.decode ("utf8") #? Q
        print (hashed_utf8)


        new_user = cls (username = username, password = hashed_utf8, email = email, first_name = first_name, last_name = last_name )
         
        db.session.add(new_user);

        return new_user;

    @classmethod
    def authenticate (cls, username, pwd):
        """Authenticate a user. 
        Return user if the username and password is a match
        else return False
        """

        u = User.query.get(username)

        if u and bcrypt.check_password_hash(u.password, pwd):
            return u
        else:
            return False
    
    @property
    def full_name(self):
        """Return full name of user"""
        return (f"{self.first_name} {self.last_name}")

class Feedback(db.Model):
    """Feedback model"""

    __tablename__ = "feedbacks";

    id = db.Column (db.Integer, primary_key = True, autoincrement = True)
    title = db.Column (db.String(100), nullable = False)
    content = db.Column (db.Text, nullable = False)
    username = db.Column (
        db.String(20), 
        db.ForeignKey('users.username'), 
        nullable = False)


