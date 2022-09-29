import sqlalchemy as sa

from backend.core.database import Base, TimestampMixin


class Post(TimestampMixin, Base):
    __tablename__ = 'posts'

    id = sa.Column(sa.Integer, primary_key=True)

    # Пока RESTRICT, в идеале ставить в NULL
    owner_id = sa.Column(sa.Integer, sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)

    text = sa.Column(sa.Text, nullable=False)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey('posts.id', ondelete='CASCADE'), nullable=True)
    post_id = sa.Column(sa.Integer, sa.ForeignKey('posts.id', ondelete='CASCADE'), nullable=True)
