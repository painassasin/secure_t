from backend.blog.exceptions import PostNotFound
from backend.blog.repositories import InvalidPostId, PostRepository
from backend.blog.schemas import Comment, Post, PostWithUser, UpdatePost
from backend.core.exceptions import Forbidden


class NotOwner(Exception):
    ...


class BlogService:
    def __init__(self) -> None:
        self.post_repository: PostRepository = PostRepository()

    async def create_post(self, owner_id: int, text: str) -> Post:
        return Post.parse_obj(await self.post_repository.create_post(owner_id, text))

    async def create_comment(self, owner_id: int, text: str, parent_id: int) -> Comment | None:
        try:
            new_comment = await self.post_repository.create_post(
                owner_id=owner_id,
                text=text,
                parent_id=parent_id,
            )
        except InvalidPostId:
            return None
        else:
            return Comment.parse_obj(new_comment)

    async def get_all_posts(self, limit: int, offset: int) -> tuple[int, list[PostWithUser]]:
        total = await self.post_repository.get_posts_count()
        items = await self.post_repository.get_all_posts(
            limit=limit,
            offset=offset,
        )
        return total, items

    async def update_post(self, post_id: int, user_id: int, data: UpdatePost):
        if not (post := await self.post_repository.get_post_or_comment_in_db(post_id=post_id, for_update=True)):
            raise PostNotFound

        if post.owner_id != user_id:
            raise Forbidden('Only owner have to update post')

        return await self.post_repository.update_post(post_id=post_id, **data.dict())

    async def delete_post(self, post_id: int, user_id: int):
        if not (post := await self.post_repository.get_post_or_comment_in_db(post_id=post_id)):
            raise PostNotFound

        if post.owner_id != user_id:
            raise Forbidden('Only owner have to delete post')

        await self.post_repository.delete_post(post_id=post_id)
