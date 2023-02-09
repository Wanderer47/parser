from pydantic import BaseSettings


class RepositorySettings(BaseSettings):
    user: str = 'postgres'
    password: str = 'password'
    host: str = 'postgres'
    database: str = 'postgres'

class AppSettings(BaseSettings):
    repository: RepositorySettings

    class Config:
        env_prefix = 'APP'
