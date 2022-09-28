from fastapi import APIRouter, Depends

from backend.auth.schemas import User
from backend.auth.utils import auth_required
from backend.core.common import USER


router = APIRouter(prefix='/users', tags=['Users'])


@router.get('/', response_model=User, dependencies=[Depends(auth_required)])
async def get_user():
    return USER.get()
