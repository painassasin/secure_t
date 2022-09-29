from datetime import datetime

from pydantic import BaseModel


class CreatePost(BaseModel):
    text: str


class CreateComment(BaseModel):
    text: str
    parent_id: int


class PostInDB(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    owner_id: int
    text: str
    parent_id: int | None
    post_id: int | None

    class Config:
        orm_mode = True


class Post(BaseModel):
    id: int
    created_at: datetime
    owner_id: int
    text: str


class Comment(BaseModel):
    id: int
    created_at: datetime
    owner_id: int
    text: str
    parent_id: int
    post_id: int


class User(BaseModel):
    id: int
    username: str


class PostWithUser(BaseModel):
    id: int
    text: str
    created_at: datetime
    comments_count: int
    owner: User

    @classmethod
    def from_db(cls, post_id: int, text: str, created_at: datetime, comments_count: int, user_id: int, username: str):
        return cls(
            id=post_id,
            text=text,
            created_at=created_at,
            comments_count=comments_count,
            owner=User(
                id=user_id,
                username=username
            )
        )


class PostComment(BaseModel):
    id: int
    created_at: datetime
    owner: User
    text: str
    comments: list = []

    @classmethod
    def transform_tree(cls, comments: list, parent_id: int | None = None) -> list[dict]:
        result = []

        for comment in comments:

            # 'RowMapping' object does not support item assignment
            comment = dict(comment)

            if 'owner' not in comment:
                user_id = comment['user_id']
                username = comment['username']
                comment['owner'] = {'id': user_id, 'username': username}
            if comment['parent_id'] == parent_id:
                comment['comments'] = cls.transform_tree(comments, comment['id'])
                result.append(comment)

        return result


class PostWithComments(PostWithUser):
    comments: list[PostComment] = []


class UpdatePost(BaseModel):
    text: str
