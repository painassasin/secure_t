from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from backend.auth.schemas import Token, User, UserCreate
from backend.core.container import auth_service
from backend.core.security import create_access_token, get_current_user


router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/signup/', response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
):
    return await auth_service.create_user(user_in)


@router.post('/signin/', response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = await auth_service.authenticate(form_data)
    return {'access_token': create_access_token(username=user.username)}


@router.get('/me/', response_model=User)
def get_itself(
    current_user: User = Depends(get_current_user),
):
    return current_user
