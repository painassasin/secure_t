from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import IntegrityError

from backend.auth.models import User
from backend.auth.schemas import UserInDB
from backend.core.common import BaseRepository


class UserAlreadyExists(Exception):
    ...


class UserRepository(BaseRepository):

    async def create_user(self, username: str, hashed_password: str) -> UserInDB:
        stmt = insert(User).values(username=username, password=hashed_password).returning(User)

        try:
            cursor: CursorResult = await self._db_session.execute(stmt)
            await self._db_session.commit()
        except IntegrityError:
            await self._db_session.rollback()
            self._logger.info('User already exists')
            raise UserAlreadyExists
        else:
            return UserInDB.parse_obj(cursor.mappings().one())

    async def get_user_by_username(self, username: str) -> UserInDB | None:
        if user := (await self._db_session.execute(
            select(User).filter_by(username=username)
        )).scalar_one_or_none():
            return UserInDB.from_orm(user)
