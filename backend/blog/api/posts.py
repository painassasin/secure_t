from fastapi import APIRouter, Depends
from starlette import status

from backend.auth.schemas import User
from backend.blog.exceptions import PostNotFound
from backend.blog.schemas import CreatePost, Post, PostWithComments, PostWithUser, UpdatePost
from backend.core.container import blog_service, post_repository
from backend.core.pagination import LimitOffsetPagination, Page
from backend.core.security import get_current_user


router = APIRouter()


@router.post('/', response_model=Post, status_code=status.HTTP_201_CREATED)
async def create_post(
    data: CreatePost,
    user: User = Depends(get_current_user),
):
    return await blog_service.create_post(owner_id=user.id, text=data.text)


@router.get('/', response_model=Page[PostWithUser])
async def get_all_posts(
    pagination: LimitOffsetPagination = Depends(),
):
    total, items = await blog_service.get_all_posts(pagination.limit, pagination.offset)
    return pagination.paginate(items, total)


@router.get('/{post_id}/', response_model=PostWithComments)
async def get_single_post(post_id: int):
    if not (post := await post_repository.get_single_post(post_id=post_id)):
        raise PostNotFound
    return post


@router.patch('/{post_id}/', response_model=Post)
async def update_post(
    post_id: int,
    data: UpdatePost,
    user: User = Depends(get_current_user),
):
    return await blog_service.update_post(post_id=post_id, user_id=user.id, data=data)


@router.delete('/{post_id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    user: User = Depends(get_current_user),
):
    await blog_service.delete_post(post_id=post_id, user_id=user.id)
