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

    def __repr__(self):
        return '<User %r>' % self.username