from pathlib import Path
from typing import Any

from pydantic import BaseSettings, PostgresDsn, validator


BASE_DIR = Path(__file__).parent.parent.parent.resolve()


class AppBaseConfig(BaseSettings):
    class Config:
        env_file = BASE_DIR.joinpath('.env')
        env_file_encoding = 'utf-8'


class DBConfig(AppBaseConfig):
    HOST: str = '127.0.0.1'
    USER: str
    PASSWORD: str
    DB: str
    DB_TEST: str | None = None
    SQL_ECHO: bool = False
    URI: PostgresDsn | None = None

    @validator('URI', pre=True)
    def build_pg_dsn(cls, v: str | None, values: dict[str, Any]) -> str:
        if isinstance(v, str):
            return v

        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            user=values['USER'],
            password=values['PASSWORD'],
            host=values.get('HOST', '127.0.0.1'),
            path='/' + values.get('DB', ''),
        )

    @validator('DB_TEST', pre=True)
    def build_test_db_name(cls, v: str | None, values: dict[str, Any]) -> str:
        if not v:
            if db_name := values.get('DB'):
                return db_name + '_test'
        return 'test'

    class Config:
        env_prefix = 'POSTGRES_'


class JWTConfig(AppBaseConfig):
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15

    class Config:
        env_prefix = 'JWT_'


class Settings(AppBaseConfig):
    DEBUG: bool = False
    SECRET_KEY: str

    DB = DBConfig()
    JWT = JWTConfig()


settings = Settings()
