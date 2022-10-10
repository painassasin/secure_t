from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from backend.auth.schemas import OAuth2PasswordRequestBody, Token, TokenData
from backend.auth.services import AuthService
from backend.auth.utils import get_access_token
from backend.core.exceptions import BadRequest


router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/signup/', response_model=Token)
async def signup(
    data: OAuth2PasswordRequestBody = Depends(),
    user_service: AuthService = Depends(),
):
    if not (user := await user_service.create_user(data)):
        raise BadRequest('User already exists')

    return {'access_token': get_access_token(token_data=TokenData.parse_obj(user))}


@router.post('/signin/', response_model=Token)
async def signin(
    data: OAuth2PasswordRequestBody = Depends(),
    user_service: AuthService = Depends(),
):
    return {
        'access_token': await user_service.signin_user(username=data.username, password=data.password),
    }


@router.post('/signin/form/', response_model=Token, include_in_schema=False)
async def signin_form(
    data: OAuth2PasswordRequestForm = Depends(),
    user_service: AuthService = Depends(),
):
    return {  # pragma: no cover
        'access_token': await user_service.signin_user(username=data.username, password=data.password),
    }
