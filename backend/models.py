import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

from backend.core.database import TimestampMixin


Base = declarative_base()


class User(TimestampMixin, Base):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(120), unique=True, index=True, nullable=False)
    password = sa.Column(sa.String(120), nullable=False)
    # TODO: Добавить поле is_active: bool для удаления


class Post(TimestampMixin, Base):
    __tablename__ = 'posts'
    __table_args__ = (
        sa.CheckConstraint('id <> parent_id', name='ck_parent_id_does_not_refer_itself'),
    )

    id = sa.Column(sa.Integer, primary_key=True)
    owner_id = sa.Column(sa.Integer, sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False, index=True)
    text = sa.Column(sa.Text, nullable=False)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey('posts.id', ondelete='CASCADE'), nullable=True, index=True)
