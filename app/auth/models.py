from app import db
from sqlalchemy.orm import relationship


# Define a base model for other database tables to inherit
class Base(db.Model):

    __abstract__  = True

    id            = db.Column(db.Integer, autoincrement=True, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())


class User(Base, db.Model):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True} 

    username = db.Column(db.String(80), unique=True, nullable=False)    
    email = db.Column(db.String(120), unique=True, nullable=False)    
    password = db.Column(db.String(256), nullable=False)    
    clusters = relationship("Cluster", cascade="save-update, merge, delete")

    @staticmethod
    def is_existed(username):
        user = User.query.filter_by(username=username).first()
        if user is None:
            return False
        else:
            return True

    @staticmethod
    def create_user(username, email, password, confirm_passowrd):
        flag = True
        message = ""
        if User.is_existed(username):
            flag = False
            message += "- Username is existed!\n"
        if password != confirm_passowrd:
            flag = False
            message += "- Confirm password does not match!\n"

        if flag:
            user = User(username=username, email=email, password=password)
            db.session.add(user)
            db.session.commit()

        return message

    @staticmethod
    def search_user_with_username(username):
        return User.query.filter_by(username=username).first()


    def __repr__(self):
        return '<User %r>' % self.username