import uuid

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from database.db import db


def create_partition(target, connection, **kw) -> None:
    """ creating partition by user_sign_in """
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_smart" PARTITION OF "log_history" FOR VALUES IN ('smart')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_mobile" PARTITION OF "log_history" FOR VALUES IN ('mobile')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_pc" PARTITION OF "log_history" FOR VALUES IN ('pc')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_tablet" PARTITION OF "log_history" FOR VALUES IN ('tablet')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_bot" PARTITION OF "log_history" FOR VALUES IN ('bot')"""
    )


users_roles = db.Table(
    'users_roles',
    db.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False),
    db.Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE")),
    db.Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id', ondelete="CASCADE"))
)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    login = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.relationship('Role', secondary=users_roles, backref='users', cascade="all, delete")

    def __repr__(self):
        return f'<User {self.login}>'


class LogHistory(db.Model):
    __tablename__ = 'log_history'
    __table_args__ = (
        UniqueConstraint('id', 'user_device_type'),
        {
            'postgresql_partition_by': 'LIST (user_device_type)',
            'listeners': [('after_create', create_partition)],
        }
    )

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), ForeignKey(User.id, ondelete="CASCADE"), nullable=False)
    user_agent = db.Column(db.Text, nullable=False)
    login_time = db.Column(db.DateTime, nullable=False)
    user_device_type = db.Column(db.Text, primary_key=True)


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String(30), unique=True, nullable=False)

    def __repr__(self):
        return f'<Role {self.name}>'


class SocialAccount(db.Model):
    __tablename__ = 'social_account'

    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, unique=True, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    user = db.relationship(User, backref=db.backref('social_accounts', lazy=True))

    social_id = db.Column(db.Text, nullable=False)
    social_name = db.Column(db.Text, nullable=False)

    __table_args__ = (db.UniqueConstraint('social_id', 'social_name', name='social_pk'),)

    def __repr__(self):
        return f'<SocialAccount {self.social_name}:{self.user_id}>'