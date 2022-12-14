import logging
from datetime import datetime, timedelta, timezone
from enum import Enum, unique

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from passlib.context import CryptContext
from passlib.exc import UnknownHashError

from backend.auth.exceptions import InvalidCredentials
from backend.auth.repositories import UserRepository
from backend.auth.schemas import User
from backend.core import settings


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/signin/')
logger = logging.getLogger(__name__)
user_repository = UserRepository()


@unique
class TokenType(Enum):
    ACCESS = 'access_token'


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except UnknownHashError as e:
        logger.warning(e)
        return False


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def _create_token(token_type: TokenType, lifetime: timedelta, sub: str) -> str:
    now = datetime.now(tz=timezone.utc)
    return jwt.encode(
        payload={
            'type': token_type.value,
            'exp': now + lifetime,
            'iat': now,
            'sub': sub
        },
        key=settings.SECRET_KEY,
        algorithm=settings.JWT.ALGORITHM
    )


def create_access_token(*, username: str) -> str:
    return _create_token(
        token_type=TokenType.ACCESS,
        lifetime=timedelta(minutes=settings.JWT.ACCESS_TOKEN_EXPIRE_MINUTES),
        sub=username,
    )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(jwt=token, key=settings.SECRET_KEY, algorithms=[settings.JWT.ALGORITHM])
    except PyJWTError as e:
        logger.debug('Failed to decode token: %s', e)
        raise InvalidCredentials
    else:
        if not (username := payload.get('sub')):
            logger.warning('Invalid payload: %s', payload)
            raise InvalidCredentials
        if not (user := await user_repository.get_user_by_username(username=username)):
            logger.debug('User %s not found', username)
            raise InvalidCredentials
        return User.parse_obj(user)
