import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from database.db import db


users_roles = db.Table(
    'users_roles',
    db.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False),
    db.Column('user_id', UUID(as_uuid=True), ForeignKey('users.id')),
    db.Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'))
)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    login = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.relationship('Role', secondary=users_roles, backref='users')

    def __repr__(self):
        return f'<User {self.login}>'


class LogHistory(db.Model):
    __tablename__ = 'log_history'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), ForeignKey(User.id))
    user_agent = db.Column(db.String, nullable=False)
    login_time = db.Column(db.DateTime, nullable=False)


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String, unique=True, nullable=False)
    # user = db.relationship('User', secondary=users_roles, backref='roles')

    def __repr__(self):
        return f'<Role {self.name}>'
