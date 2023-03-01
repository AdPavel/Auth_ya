import pathlib
from pydantic import BaseSettings
from typing import Any


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

    # Yandex section
    yandex_client_id: str
    yandex_client_secret: str
    yandex_authorization_base_url: str
    yandex_token_url: str
    yandex_info_url: str

    # Google section
    google_client_id: str
    google_client_secret: str
    google_authorization_base_url: str
    google_token_url: str
    google_info_url: str
    google_scope: list[str]

    redirect_uri: str

    class Config:

        env_file = f"{pathlib.Path(__file__).resolve().parent.parent.parent.parent}/.env"
        env_file_encoding = 'utf-8'

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> Any:
            if field_name == 'google_scope':
                return [x for x in raw_val.split(',')]
            return cls.json_loads(raw_val)


settings = Base()
