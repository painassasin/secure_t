from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from backend.auth.schemas import User
from backend.auth.utils import auth_required
from backend.blog.schemas import Comment, CreateComment
from backend.blog.services import BlogService


router = APIRouter(prefix='/comments', tags=['Blog'])


@router.post('/', response_model=Comment, status_code=status.HTTP_201_CREATED)
async def create_comment(
    data: CreateComment,
    user: User = Depends(auth_required),
    blog_service: BlogService = Depends(),
):
    if not (comment := await blog_service.create_comment(
        owner_id=user.id,
        text=data.text,
        parent_id=data.parent_id,
    )):
        raise HTTPException(detail='Invalid parentId', status_code=status.HTTP_400_BAD_REQUEST)
    return comment
