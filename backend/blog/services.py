from backend.blog.repositories import PostRepository
from backend.blog.schemas import Post


class BlogService:
    def __init__(self) -> None:
        self._post_repository: PostRepository = PostRepository()

    async def create_post(self, owner_id: int, text: str) -> Post:
        return Post.parse_obj(await self._post_repository.create_post(owner_id, text))
