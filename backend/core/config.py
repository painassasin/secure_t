from typing import Any

from pydantic import BaseSettings, PostgresDsn, validator


class AppSettings(BaseSettings):
    DEBUG: bool = False

    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URI: PostgresDsn | None = None
    POSTGRES_DB_ECHO: bool = False

    @validator('DATABASE_URI', pre=True)
    def assemble_db_connection(cls, v: str | None, values: dict[str, Any]) -> str:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            user=values.get('POSTGRES_USER'),
            password=values.get('POSTGRES_PASSWORD'),
            host=values.get('POSTGRES_HOST'),
            path='/' + values.get('POSTGRES_DB', ''),
        )

    SECRET_KEY: str
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file_encoding = 'utf-8'
        env_file = '.env'


settings = AppSettings()
