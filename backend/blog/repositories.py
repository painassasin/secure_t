from sqlalchemy import desc, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased

from backend.auth.models import User
from backend.blog.models import Post
from backend.blog.schemas import PostInDB, PostWithUser
from backend.core.common import BaseRepository


class InvalidPostId(Exception):
    ...


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
            raise InvalidPostId
        else:
            return PostInDB.parse_obj(cursor.mappings().one())

    async def get_all_posts(self, limit: int, offset: int) -> list[PostWithUser]:
        p1 = aliased(Post)
        p2 = aliased(Post)
        comments_cte = select(
            p1.id.label('post_id'),
            func.count(p2.post_id).label('comments_count')
        ).outerjoin(
            p2, p1.id == p2.post_id
        ).filter(p1.post_id.is_(None)).group_by(p1.id).cte('comments_cte')

        stmt = select(
            Post.id.label('post_id'),
            Post.text,
            Post.created_at,
            comments_cte.c.comments_count,
            User.id.label('user_id'),
            User.username
        ).join(
            User, User.id == Post.owner_id
        ).outerjoin(
            comments_cte, comments_cte.c.post_id == Post.id
        ).filter(Post.post_id.is_(None)).order_by(desc(Post.created_at)).limit(limit).offset(offset)

        return [
            PostWithUser.from_db(**row)
            for row in (await self._db_session.execute(stmt)).mappings().all()
        ]

    async def get_posts_count(self) -> int:
        return (await self._db_session.execute(
            select(func.count(Post.id)).filter(Post.post_id.is_(None))
        )).scalar()
