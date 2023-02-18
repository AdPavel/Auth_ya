import pathlib
from pydantic import BaseSettings


class Base(BaseSettings):
    # Elastic section
    els_port: int
    els_host: str

    # Redis section
    redis_host: str
    redis_port: int

    test_service_url: str

    class Config:

        env_file = f"{pathlib.Path(__file__).resolve().parent.parent.parent}/.env"
        env_file_encoding = 'utf-8'


settings = Base()
