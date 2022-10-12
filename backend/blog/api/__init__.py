from fastapi import APIRouter

from .comments import router as comments_router
from .posts import router as posts_router


router = APIRouter(prefix='/blog', tags=['Blog'])
router.include_router(router=comments_router, prefix='/comments')
router.include_router(router=posts_router, prefix='/posts')
