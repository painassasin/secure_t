from backend.auth.exceptions import InvalidCredentials
from backend.auth.repositories import UserAlreadyExists, UserRepository
from backend.auth.schemas import OAuth2PasswordRequestBody, TokenData, UserInDB
from backend.auth.utils import get_access_token, get_password_hash, verify_password


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

    async def signin_user(self, username: str, password: str) -> str:
        user = await self._user_repository.get_user_by_username(username)
        if not user or not verify_password(password, user.password):
            raise InvalidCredentials
        return get_access_token(token_data=TokenData.parse_obj(user))
