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
