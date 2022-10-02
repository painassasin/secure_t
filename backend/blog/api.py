from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status

from backend.auth.schemas import User
from backend.auth.utils import auth_required
from backend.blog.repositories import PostRepository
from backend.blog.schemas import Comment, CreateComment, CreatePost, Post, PostWithComments, PostWithUser, UpdatePost
from backend.blog.services import BlogService, NotOwner, PostNotFound
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
    post_repository: PostRepository = Depends(),
):
    if not (post := await post_repository.get_post_in_db(post_id)):
        raise HTTPException(detail='Post not found', status_code=status.HTTP_404_NOT_FOUND)

    if not (comment := await blog_service.create_comment(
        owner_id=user.id,
        text=data.text,
        parent_id=data.parent_id,
        post_id=post.id
    )):
        raise HTTPException(detail='Invalid parentId', status_code=status.HTTP_400_BAD_REQUEST)
    return comment


@router.patch('/{post_id}/', response_model=Post)
async def update_post(
    post_id: int,
    data: UpdatePost,
    user: User = Depends(auth_required),
    blog_service: BlogService = Depends(),
):
    try:
        return await blog_service.update_post(post_id=post_id, user_id=user.id, data=data)
    except PostNotFound:
        raise HTTPException(detail='Post not found', status_code=status.HTTP_404_NOT_FOUND)
    except NotOwner:
        raise HTTPException(detail='Only owner have to update post', status_code=status.HTTP_403_FORBIDDEN)


@router.delete('/{post_id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    user: User = Depends(auth_required),
    post_repository: PostRepository = Depends(),
):
    if not (post := await post_repository.get_post_or_comment_in_db(post_id=post_id)):
        raise HTTPException(detail='Post not found', status_code=status.HTTP_404_NOT_FOUND)

    if post.owner_id != user.id:
        raise HTTPException(detail='Only owner have to delete post', status_code=status.HTTP_403_FORBIDDEN)

    await post_repository.delete_post(post_id)
