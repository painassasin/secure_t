from fastapi import APIRouter, Depends
from starlette import status

from backend.auth.schemas import User
from backend.blog.schemas import Comment, CreateComment
from backend.core.container import blog_service
from backend.core.exceptions import BadRequest
from backend.core.security import get_current_user


router = APIRouter()


@router.post('/', response_model=Comment, status_code=status.HTTP_201_CREATED)
async def create_comment(
    data: CreateComment,
    user: User = Depends(get_current_user),
):
    if not (comment := await blog_service.create_comment(
        owner_id=user.id,
        text=data.text,
        parent_id=data.parent_id,
    )):
        raise BadRequest('Invalid parentId')
    return comment
