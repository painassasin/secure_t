from backend.blog.repositories import InvalidPostId, PostRepository
from backend.blog.schemas import Comment, Post, PostWithUser, UpdatePost


class PostNotFound(Exception):
    ...


class NotOwner(Exception):
    ...


class BlogService:
    def __init__(self) -> None:
        self._post_repository: PostRepository = PostRepository()

    async def create_post(self, owner_id: int, text: str) -> Post:
        return Post.parse_obj(await self._post_repository.create_post(owner_id, text))

    async def create_comment(self, owner_id: int, text: str, parent_id: int) -> Comment | None:
        try:
            new_comment = await self._post_repository.create_post(
                owner_id=owner_id,
                text=text,
                parent_id=parent_id,
            )
        except InvalidPostId:
            return None
        else:
            # TODO: Без этого условия можно будет создать комментарий ссылающийся сам на себя, однако он создался (
            if new_comment.id != new_comment.parent_id:
                return Comment.parse_obj(new_comment)
            else:
                await self._post_repository.delete_post(new_comment.id)

    async def get_all_posts(self, limit: int, offset: int) -> tuple[int, list[PostWithUser]]:
        total = await self._post_repository.get_posts_count()
        items = await self._post_repository.get_all_posts(
            limit=limit,
            offset=offset,
        )
        return total, items

    async def update_post(self, post_id: int, user_id: int, data: UpdatePost):
        if not (post := await self._post_repository.get_post_or_comment_in_db(post_id=post_id)):
            raise PostNotFound

        if post.owner_id != user_id:
            raise NotOwner

        return await self._post_repository.update_post(post_id=post_id, owner_id=user_id, **data.dict())
