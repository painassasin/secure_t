import asyncio
import logging
import random

from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import async_session
from backend.core.security import get_password_hash
from backend.models import Post, User


USERS_COUNT: int = 10
POSTS_COUNT: int = 15
COMMENTS_1_COUNT: int = 20
COMMENTS_2_COUNT: int = 20
COMMENTS_3_COUNT: int = 20

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def load_fixtures(session: AsyncSession) -> None:
    users = [User(username=f'user_{i}', password=get_password_hash('123456')) for i in range(USERS_COUNT)]
    session.add_all(users)
    await session.flush(users)

    posts = [
        Post(owner_id=random.choice([user.id for user in users]), text=f'post_{i}')
        for i in range(POSTS_COUNT)
    ]
    session.add_all(posts)
    await session.flush(posts)

    comments_1 = [
        Post(
            owner_id=random.choice([user.id for user in users]),
            text=f'comment_1_{i}',
            parent_id=random.choice([post.id for post in posts])
        )
        for i in range(COMMENTS_1_COUNT)
    ]
    session.add_all(comments_1)
    await session.flush(comments_1)

    comments_2 = [
        Post(
            owner_id=random.choice([user.id for user in users]),
            text=f'comment_2_{i}',
            parent_id=random.choice([comment.id for comment in comments_1])
        )
        for i in range(COMMENTS_2_COUNT)
    ]
    session.add_all(comments_2)
    await session.flush(comments_2)

    comments_3 = [
        Post(
            owner_id=random.choice([user.id for user in users]),
            text=f'comment_3_{i}',
            parent_id=random.choice([comment.id for comment in comments_2])
        )
        for i in range(COMMENTS_3_COUNT)
    ]
    session.add_all(comments_3)
    await session.flush(comments_3)


async def main():
    async with async_session() as db_session:
        try:
            await load_fixtures(db_session)
            await db_session.commit()
        except DBAPIError as e:
            logging.error('Failed to load fixtures due error %s', e)
            await db_session.rollback()
        else:
            logging.info('Fixtures successfully loaded')
        finally:
            await db_session.close()


if __name__ == '__main__':
    asyncio.run(main())
