import pathlib
from pydantic import BaseSettings


class Base(BaseSettings):

    # postgres
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int
    postgres_db: str

    # Redis section
    redis_host: str
    redis_port: int

    # JWT section
    secret_key: str
    access_token_expires_hours: int
    refresh_token_expires_days: int

    class Config:

        env_file = f"{pathlib.Path(__file__).resolve().parent.parent.parent.parent}/.env"
        env_file_encoding = 'utf-8'


settings = Base()
