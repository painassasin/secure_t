from fastapi import APIRouter, Depends
from starlette import status

from backend.auth.schemas import User
from backend.auth.utils import auth_required
from backend.blog.schemas import CreatePost, Post
from backend.blog.services import BlogService


router = APIRouter(prefix='/posts', tags=['Blog'])


@router.post('/', response_model=Post, status_code=status.HTTP_201_CREATED)
async def create_post(
    data: CreatePost,
    user: User = Depends(auth_required),
    blog_service: BlogService = Depends(),
):
    return await blog_service.create_post(owner_id=user.id, text=data.text)
