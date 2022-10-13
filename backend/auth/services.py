from fastapi.security import OAuth2PasswordRequestForm

from backend.auth.exceptions import InvalidCredentials, UserAlreadyExists
from backend.auth.repositories import UsernameAlreadyExists, UserRepository
from backend.auth.schemas import UserCreate, UserInDB
from backend.core.security import get_password_hash, verify_password


class AuthService:
    def __init__(self):
        self.user_repository = UserRepository()

    async def create_user(self, user_in: UserCreate) -> UserInDB:
        hashed_password: str = get_password_hash(user_in.password)
        try:
            return await self.user_repository.create_user(
                username=user_in.username,
                hashed_password=hashed_password
            )
        except UsernameAlreadyExists:
            raise UserAlreadyExists

    async def authenticate(self, form_data: OAuth2PasswordRequestForm) -> UserInDB:
        if not (user := await self.user_repository.get_user_by_username(username=form_data.username)):
            raise InvalidCredentials
        if not verify_password(form_data.password, user.password):
            raise InvalidCredentials
        return user
