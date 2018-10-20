from app import db
from sqlalchemy.sql import func
import datetime
from sqlalchemy import Table, Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship

# Define a base model for other database tables to inherit
class Base(db.Model):

    __abstract__  = True

    id            = db.Column(db.Integer, autoincrement=True, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())


class VirtualMachine(Base, db.Model):
    __tablename__ = 'virtual_machine'
    __table_args__ = {'extend_existing': True} 

    name = db.Column(db.String(50), nullable=False)
    vm_type = db.Column(db.String(20), nullable=False)
    public_ip = db.Column(db.String(20), unique=True, nullable=True)
    private_ip = db.Column(db.String(20), unique=True, nullable=False)
    cluster_id = db.Column(db.Integer, db.ForeignKey('cluster.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    def __repr__(self):
        return '<Name %r>' % self.name

    
class Cluster(Base, db.Model):
    __tablename__ = 'cluster'
    __table_args__ = {'extend_existing': True} 

    jupyter_url = db.Column(db.String(256), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    vms = relationship("VirtualMachine", cascade="save-update, merge, delete")


    def __repr__(self):
        return '<Jupyter URL %r>' % self.jupyter_url

class CeleryTask(db.Model):
    __tablename__ = 'celery_task'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.String(100), primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    task_type = db.Column(db.String(50), nullable=False)
    result = db.Column(db.TEXT, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
