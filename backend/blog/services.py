from backend.blog.repositories import InvalidPostId, PostRepository
from backend.blog.schemas import Comment, Post, PostWithComments, PostWithUser


class BlogService:
    def __init__(self) -> None:
        self._post_repository: PostRepository = PostRepository()

    async def create_post(self, owner_id: int, text: str) -> Post | None:
        try:
            new_post = await self._post_repository.create_post(owner_id, text)
        except InvalidPostId:
            return None
        else:
            return Post.parse_obj(new_post)

    async def create_comment(self, owner_id: int, text: str, parent_id: int, post_id: int) -> Comment | None:
        try:
            new_comment = await self._post_repository.create_post(
                owner_id=owner_id,
                text=text,
                parent_id=parent_id,
                post_id=post_id,
            )
        except InvalidPostId:
            return None
        else:
            return Comment.parse_obj(new_comment)

    async def get_all_posts(self, limit: int, offset: int) -> tuple[int, list[PostWithUser]]:
        total = await self._post_repository.get_posts_count()
        items = await self._post_repository.get_all_posts(
            limit=limit,
            offset=offset,
        )
        return total, items

    async def get_post(self, post_id: int) -> PostWithComments | None:
        if post := await self._post_repository.get_post(post_id):
            post_with_comments: PostWithComments = PostWithComments.parse_obj(post)
            post_with_comments.comments = await self._post_repository.get_post_comments(post_id)
            return post_with_comments
