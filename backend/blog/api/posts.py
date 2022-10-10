from fastapi import APIRouter, Depends, Query
from starlette import status

from backend.auth.schemas import User
from backend.auth.utils import auth_required
from backend.blog.exceptions import PostNotFound
from backend.blog.repositories import PostRepository
from backend.blog.schemas import CreatePost, Post, PostWithComments, PostWithUser, UpdatePost
from backend.blog.services import BlogService
from backend.core.pagination import Page, paginate


router = APIRouter(prefix='/posts', tags=['Blog'])


@router.post('/', response_model=Post, status_code=status.HTTP_201_CREATED)
async def create_post(
    data: CreatePost,
    user: User = Depends(auth_required),
    blog_service: BlogService = Depends(),
):
    return await blog_service.create_post(owner_id=user.id, text=data.text)


@router.get('/', response_model=Page[PostWithUser])
async def get_all_posts(
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    blog_service: BlogService = Depends(),
):
    total, items = await blog_service.get_all_posts(limit, offset)
    return paginate(items, limit, offset, total)


@router.get('/{post_id}/', response_model=PostWithComments)
async def get_single_post(
    post_id: int,
    post_repository: PostRepository = Depends(),
):
    if not (post := await post_repository.get_single_post(post_id=post_id)):
        raise PostNotFound
    return post


@router.patch('/{post_id}/', response_model=Post)
async def update_post(
    post_id: int,
    data: UpdatePost,
    user: User = Depends(auth_required),
    blog_service: BlogService = Depends(),
):
    return await blog_service.update_post(post_id=post_id, user_id=user.id, data=data)


@router.delete('/{post_id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    user: User = Depends(auth_required),
    post_repository: PostRepository = Depends(),
    blog_service: BlogService = Depends(),
):
    await blog_service.delete_post(post_id=post_id, user_id=user.id)
