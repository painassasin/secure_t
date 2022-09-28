from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import IntegrityError

from backend.blog.models import Post
from backend.blog.schemas import PostInDB
from backend.core.common import BaseRepository


class PostRepository(BaseRepository):

    async def create_post(
        self,
        owner_id: int,
        text: str,
        parent_id: int | None = None,
        post_id: int | None = None
    ) -> PostInDB:
        stmt = insert(Post).values(
            owner_id=owner_id,
            text=text,
            parent_id=parent_id,
            post_id=post_id
        ).returning(Post)

        try:
            cursor: CursorResult = await self._db_session.execute(stmt)
            await self._db_session.commit()
        except IntegrityError as e:
            await self._db_session.rollback()
            self._logger.info(e)
            raise  # TODO: need exception
        else:
            return PostInDB.parse_obj(cursor.mappings().one())
