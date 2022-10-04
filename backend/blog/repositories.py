from sqlalchemy import delete, desc, func, literal, select, update
from sqlalchemy.dialects.postgresql import Insert, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased
from sqlalchemy.sql import Select
from sqlalchemy.sql.selectable import CTE

from backend.auth.models import User
from backend.blog.models import Post
from backend.blog.schemas import PostInDB, PostWithComments, PostWithUser
from backend.core.repository import BaseRepository


class InvalidPostId(Exception):
    ...


class PostRepository(BaseRepository):

    async def create_post(
        self,
        owner_id: int,
        text: str,
        parent_id: int | None = None,
    ) -> PostInDB:
        """
        INSERT INTO posts p (owner_id, text, parent_id)
        VALUES (:owner_id, :text, :parent_id)
        RETURNING (p.id, p.created_at, p.updated_at, p.owner_id, p.text, p.parent_id)
        """
        stmt: Insert = insert(Post).values(
            owner_id=owner_id,
            text=text,
            parent_id=parent_id,
        ).returning(Post)

        try:
            post = PostInDB.parse_obj((await self._db_session.execute(stmt)).mappings().one())
            if post.id == parent_id:
                await self.delete_post(post_id=post.id)
                raise ValueError(
                    'Пост не может ссылаться на самого себя, parent_id=%s, post_id=%d',
                    parent_id, post.id
                )
        except (ValueError, IntegrityError) as e:
            await self._db_session.rollback()
            self._logger.info(e)
            raise InvalidPostId
        else:
            await self._db_session.commit()
            return post

    async def get_all_posts(self, limit: int, offset: int) -> list[PostWithUser]:
        """
        WITH RECURSIVE t AS (
            SELECT p1.id, p1."text", p1.owner_id, p1.created_at, p1.id AS child_id, 0 cntr
            FROM posts p1
            WHERE p1.parent_id IS NULL
            UNION ALL
            SELECT t.id, t."text", t.owner_id, t.created_at, p2.id, cntr + 1
            FROM t
            JOIN posts p2 ON p2.parent_id = t.child_id
        )
        SELECT t.id, t."text", t.created_at, count(*), u.id "user_id", u.username
        FROM t LEFT JOIN users u ON u.id = t.owner_id
        WHERE cntr != 0
        GROUP BY t.id, t."text", t.created_at, u.id, u.username
        """
        p1 = aliased(Post, name='p1')
        t_cte: CTE = select(
            p1.id,
            p1.text,
            p1.owner_id,
            p1.created_at,
            p1.id.label('child_id'),
            literal(0).label('cntr')
        ).filter(p1.parent_id.is_(None)).cte('t', recursive=True)

        p2 = aliased(Post, name='p2')
        t_cte = t_cte.union_all(
            select(
                t_cte.c.id,
                t_cte.c.text,
                t_cte.c.owner_id,
                t_cte.c.created_at,
                p2.id,
                t_cte.c.cntr + 1,
            ).join(
                p2, p2.parent_id == t_cte.c.child_id
            )
        )

        stmt: Select = select(
            t_cte.c.id,
            t_cte.c.text,
            t_cte.c.created_at,
            (func.count() - 1).label('comments_count'),
            User.id.label('user_id'),
            User.username
        ).join(
            User, User.id == t_cte.c.owner_id
        ).group_by(
            t_cte.c.id, t_cte.c.text, t_cte.c.created_at, User.id, User.username
        ).order_by(
            desc(t_cte.c.created_at)
        ).limit(limit).offset(offset)

        return [
            PostWithUser(**row)
            for row in (await self._db_session.execute(stmt)).mappings().all()
        ]

    async def get_posts_count(self) -> int:
        """
        SELECT COUNT(*) FROM posts p WHERE p.parent_id IS NULL
        """
        return (await self._db_session.execute(
            select(func.count()).filter(Post.parent_id.is_(None))
        )).scalar()

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
            select(Post).filter(Post.id == post_id, Post.parent_id.is_(None))
        )).scalar_one_or_none():
            return PostInDB.from_orm(post)

    async def delete_post(self, post_id: int) -> None:
        """
        DELETE FROM posts p WHERE p.id == :post_id
        """
        await self._db_session.execute(delete(Post).filter(Post.id == post_id))
        await self._db_session.commit()

    async def get_single_post(self, post_id: int) -> PostWithComments | None:
        """
        WITH RECURSIVE cte(id, parent_id, "text", owner_id, created_at) AS (
                SELECT p.id, p.parent_id, p."text", p.owner_id, p.created_at
                FROM posts p WHERE p.id = :post_id
            UNION ALL
                SELECT t.id, t.parent_id, t."text", t.owner_id, t.created_at
                FROM posts t JOIN cte ON cte.id = t.parent_id
        )
        SELECT cte.created_at, cte.id, cte.parent_id, cte."text", u.id "user_id", u.username
        FROM cte LEFT JOIN users u ON u.id = cte.owner_id
        ORDER_BY cte.created_at DESC
        """

        p = aliased(Post, name='p')
        cte: CTE = select(
            p.id, p.parent_id, p.text, p.owner_id, p.created_at
        ).filter(p.id == post_id).cte('cte', recursive=True)

        t = aliased(Post, name='t')
        cte = cte.union_all(
            select(
                t.id, t.parent_id, t.text, t.owner_id, t.created_at
            ).join(cte, cte.c.id == t.parent_id)
        )

        stmt: Select = select(
            cte.c.created_at,
            cte.c.id,
            cte.c.parent_id,
            cte.c.text,
            User.id.label('user_id'),
            User.username
        ).join(
            User, User.id == cte.c.owner_id
        ).order_by(
            desc(cte.c.created_at)
        )

        return PostWithComments.from_db_list(
            (await self._db_session.execute(stmt)).mappings().all()
        )
