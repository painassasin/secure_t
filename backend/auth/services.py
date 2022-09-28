from backend.auth.repositories import UserAlreadyExists, UserRepository
from backend.auth.schemas import OAuth2PasswordRequestBody, UserInDB
from backend.auth.utils import get_password_hash


class AuthService:

    def __init__(self) -> None:
        self._user_repository: UserRepository = UserRepository()

    async def create_user(self, data: OAuth2PasswordRequestBody) -> UserInDB | None:
        hashed_password: str = get_password_hash(data.password)
        try:
            return await self._user_repository.create_user(
                username=data.username,
                hashed_password=hashed_password
            )
        except UserAlreadyExists:
            return None
