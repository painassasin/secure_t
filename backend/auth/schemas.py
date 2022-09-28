from datetime import datetime

from fastapi import Body
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel


class OAuth2PasswordRequestBody(OAuth2PasswordRequestForm):
    def __init__(
        self,
        grant_type: str = Body(default=None, regex='password'),
        username: str = Body(),
        password: str = Body(),
        scope: str = Body(default=''),
        client_id: str | None = Body(default=None),
        client_secret: str | None = Body(default=None),
    ):
        super().__init__(
            grant_type=grant_type,
            username=username,
            password=password,
            scope=scope,
            client_id=client_id,
            client_secret=client_secret,

        )


class UserInDB(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    username: str
    password: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int
    username: str


class User(BaseModel):
    id: int
    username: str
