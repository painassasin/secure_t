from pydantic import parse_obj_as
from sqlalchemy import case, delete, desc, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased
from sqlalchemy.sql import Select

from backend.auth.models import User
from backend.blog.models import Post
from backend.blog.schemas import PostComment, PostInDB, PostWithUser
from backend.core.repository import BaseRepository


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
        comments_cte = self._comments_cte()
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

    async def get_post(self, post_id: int) -> PostWithUser | None:
        comments_cte = self._comments_cte(post_id=post_id)
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
        ).filter(Post.post_id.is_(None), Post.id == post_id)

        if result := (await self._db_session.execute(stmt)).mappings().one_or_none():
            return PostWithUser.from_db(**result)

    @staticmethod
    def _comments_cte(post_id: int | None = None) -> Select:
        p1 = aliased(Post)
        p2 = aliased(Post)
        comments_cte = select(
            p1.id.label('post_id'),
            func.count(p2.post_id).label('comments_count')
        ).outerjoin(
            p2, p1.id == p2.post_id
        ).filter(
            p1.post_id.is_(None),
        )
        if post_id:
            comments_cte = comments_cte.filter(p2.post_id == post_id)

        return comments_cte.group_by(p1.id).cte('comments_cte')

    async def get_post_comments(self, post_id: int):
        stmt = select(
            Post.id, Post.created_at, Post.text,
            case((Post.parent_id == post_id, None), else_=Post.parent_id).label('parent_id'),
            User.id.label('user_id'), User.username,
        ).join(
            User, User.id == Post.owner_id
        ).filter(
            Post.post_id == post_id
        ).order_by(desc(Post.created_at))

        results = (await self._db_session.execute(stmt)).mappings().all()
        return parse_obj_as(list[PostComment], PostComment.transform_tree(results))

    async def update_post(self, post_id: int, owner_id: int, **values) -> PostInDB:
        values['updated_at'] = func.now()
        cursor = await self._db_session.execute(
            update(Post).values(**values).filter(
                Post.id == post_id,
                Post.owner_id == owner_id,
            ).returning(Post)
        )
        await self._db_session.commit()
        return PostInDB.parse_obj(cursor.mappings().one())

    async def get_post_or_comment_in_db(self, post_id) -> PostInDB | None:
        if post := (await self._db_session.execute(
            select(Post).filter(Post.id == post_id)
        )).scalar_one_or_none():
            return PostInDB.from_orm(post)

    async def get_post_in_db(self, post_id) -> PostInDB | None:
        if post := (await self._db_session.execute(
            select(Post).filter(Post.id == post_id, Post.post_id.is_(None))
        )).scalar_one_or_none():
            return PostInDB.from_orm(post)

    async def delete_post(self, post_id) -> None:
        await self._db_session.execute(delete(Post).filter(Post.id == post_id))
        await self._db_session.commit()
