from datetime import datetime
from typing import Optional

from pydantic import BaseModel, root_validator


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

    class Config:
        orm_mode = True


class Post(BaseModel):
    id: int
    created_at: datetime
    owner_id: int
    text: str


class Comment(Post):
    parent_id: int


class User(BaseModel):
    id: int
    username: str


class PostWithUser(BaseModel):
    id: int
    text: str
    created_at: datetime
    comments_count: int
    owner: User

    @root_validator(pre=True)
    def set_owner(cls, values: dict):
        if 'owner' not in values:
            values['owner'] = User(id=values['user_id'], username=values['username'])
        return values


class PostComment(BaseModel):
    id: int
    created_at: datetime
    owner: User
    text: str
    comments: list['PostComment'] = []

    @root_validator(pre=True)
    def set_owner(cls, values: dict):
        if 'owner' not in values:
            values['owner'] = User(id=values['user_id'], username=values['username'])
        return values

    @classmethod
    def get_comments(cls, post_comments: list[dict], parent_id: int | None = None) -> list['PostComment']:
        results: list['PostComment'] = []

        for post_comment in post_comments.copy():
            if post_comment['parent_id'] == parent_id:
                item = cls.parse_obj(post_comment)
                item.comments = cls.get_comments(post_comments, item.id)
                results.append(item)
                post_comments.remove(post_comment)
        return results


class PostWithComments(PostWithUser):
    comments: list[PostComment] = []

    @classmethod
    def from_db_list(cls, post_comments: list[dict]) -> Optional['PostWithComments']:
        data_length = len(post_comments)
        if comments := PostComment.get_comments(post_comments):
            return cls(**comments[0].dict(), comments_count=data_length - 1)


class UpdatePost(BaseModel):
    text: str
