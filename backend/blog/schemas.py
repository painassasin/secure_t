from datetime import datetime

from pydantic import BaseModel


class CreatePost(BaseModel):
    text: str


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
