from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status

from backend.auth.schemas import User
from backend.auth.utils import auth_required
from backend.blog.schemas import Comment, CreateComment, CreatePost, Post, PostWithComments, PostWithUser
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
async def get_post_description(
    post_id: int,
    blog_service: BlogService = Depends(),
):
    if not (post := await blog_service.get_post(post_id=post_id)):
        raise HTTPException(detail='Post not found', status_code=status.HTTP_404_NOT_FOUND)
    return post


@router.post('/{post_id}/comments/', response_model=Comment, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: int,
    data: CreateComment,
    user: User = Depends(auth_required),
    blog_service: BlogService = Depends(),
):
    if not (comment := await blog_service.create_comment(
        owner_id=user.id,
        text=data.text,
        parent_id=data.parent_id,
        post_id=post_id
    )):
        raise HTTPException(detail='Invalid post or parentId', status_code=status.HTTP_400_BAD_REQUEST)
    return comment
