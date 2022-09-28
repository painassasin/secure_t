import logging
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from passlib.context import CryptContext
from pydantic import ValidationError
from starlette import status

from backend.auth.repositories import UserRepository
from backend.auth.schemas import TokenData, User
from backend.core import settings
from backend.core.common import USER


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/signin/form/')

logger = logging.getLogger(__name__)


def get_access_token(token_data: TokenData) -> str:
    data = token_data.dict()
    data['exp'] = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def auth_required(
    token: str = Depends(oauth2_scheme),
    user_repository: UserRepository = Depends(),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = TokenData(**payload)
    except (PyJWTError, ValidationError) as e:
        logger.debug(e)
        raise credentials_exception
    if not (user_in_db := await user_repository.get_user_by_username(username=token_data.username)):
        logger.debug('User not found in db: username=%s', token_data.username)
        raise credentials_exception
    user = User.parse_obj(user_in_db)
    USER.set(user)
    return user
