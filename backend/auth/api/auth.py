from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from backend.auth.repositories import UserRepository
from backend.auth.schemas import OAuth2PasswordRequestBody, Token, TokenData
from backend.auth.services import AuthService
from backend.auth.utils import get_access_token, verify_password


router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/signup/', response_model=Token)
async def signup(
    data: OAuth2PasswordRequestBody = Depends(),
    user_service: AuthService = Depends(),
):
    if not (user := await user_service.create_user(data)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User already exists',
        )

    assess_token = get_access_token(token_data=TokenData.parse_obj(user))
    return {'access_token': assess_token, 'token_type': 'bearer'}


@router.post('/signin/', response_model=Token)
async def signin(
    data: OAuth2PasswordRequestBody = Depends(),
    user_repository: UserRepository = Depends(),
):
    user = await user_repository.get_user_by_username(data.username)
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password',
        )

    assess_token = get_access_token(token_data=TokenData.parse_obj(user))
    return {'access_token': assess_token, 'token_type': 'bearer'}


@router.post('/signin/form/', response_model=Token, description='Signin via multipart form data')
async def signin_form(
    data: OAuth2PasswordRequestForm = Depends(),
    user_repository: UserRepository = Depends(),
):
    user = await user_repository.get_user_by_username(data.username)
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password',
        )

    assess_token = get_access_token(token_data=TokenData.parse_obj(user))
    return {'access_token': assess_token, 'token_type': 'bearer'}
