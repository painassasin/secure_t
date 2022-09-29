from backend.blog.repositories import PostRepository
from backend.blog.schemas import Comment, Post


class BlogService:
    def __init__(self) -> None:
        self._post_repository: PostRepository = PostRepository()

    async def create_post(self, owner_id: int, text: str) -> Post:
        return Post.parse_obj(await self._post_repository.create_post(owner_id, text))

    async def create_comment(self, owner_id: int, text: str, parent_id: int, post_id: int) -> Comment:
        return Comment.parse_obj(await self._post_repository.create_post(
            owner_id=owner_id,
            text=text,
            parent_id=parent_id,
            post_id=post_id,
        ))
