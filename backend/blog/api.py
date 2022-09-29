from fastapi import APIRouter, Depends
from starlette import status

from backend.auth.schemas import User
from backend.auth.utils import auth_required
from backend.blog.schemas import CreateComment, CreatePost, Post
from backend.blog.services import BlogService


router = APIRouter(prefix='/posts', tags=['Blog'])


@router.post('/', response_model=Post, status_code=status.HTTP_201_CREATED)
async def create_post(
    data: CreatePost,
    user: User = Depends(auth_required),
    blog_service: BlogService = Depends(),
):
    return await blog_service.create_post(owner_id=user.id, text=data.text)


@router.post('/{post_id}/comments/', status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: int,
    data: CreateComment,
    user: User = Depends(auth_required),
    blog_service: BlogService = Depends(),
):
    return await blog_service.create_comment(
        owner_id=user.id,
        text=data.text,
        parent_id=data.parent_id,
        post_id=post_id
    )
