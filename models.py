from flask_login import UserMixin
from app import db
from datetime import datetime


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    tasks_list = db.relationship('Task', backref='user')

    def __str__(self):
        return (
            f'Id: {self.id}, '
            f'Name: {self.name}, '
            f'Email: {self.email}, '
            f'Password: {self.password}'
        )


class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    # Foreign Key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    task_todo = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.now())

    def __str__(self):
        return (
            f'Id: {self.id}, '
            f'Task: {self.task}, '
            f'Date: {self.date}'
        )