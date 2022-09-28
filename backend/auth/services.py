# from typing import Iterator
# from uuid import uuid4
#
# from backend.auth.models import User
# from backend.auth.repositories import UserRepository
#
#
from backend.auth.repositories import UserRepository


class UserService:

    def __init__(self) -> None:
        self._repository: UserRepository = UserRepository()

    async def get_users(self):
        return await self._repository.get_all()
#
#     def get_user_by_id(self, user_id: int) -> User:
#         return self._repository.get_by_id(user_id)
#
#     def create_user(self) -> User:
#         uid = uuid4()
#         return self._repository.add(username=f"{uid}@email.com", password="pwd")
#
#     def delete_user_by_id(self, user_id: int) -> None:
#         return self._repository.delete_by_id(user_id)
