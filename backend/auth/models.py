import sqlalchemy as sa

from backend.core.database import Base, TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(120), unique=True, index=True, nullable=False)
    password = sa.Column(sa.String(120), nullable=False)
    # TODO: Добавить поле is_active: bool для удаления
