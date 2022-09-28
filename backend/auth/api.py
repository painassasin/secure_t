from fastapi import APIRouter, Depends

from backend.auth.services import UserService


router = APIRouter(prefix='/users', tags=['Auth'])


@router.get('/')
async def get_list(
    user_service: UserService = Depends(),
):
    return await user_service.get_users()
