from pydantic_settings import BaseSettingsModel, load_settings


class RepositorySettings(BaseSettingsModel):
    user: str = 'postgres'
    password: str = 'password'
    host: str = 'localhost'
    database: str = 'postgres'

class AppSettings(BaseSettingsModel):
    repository: RepositorySettings

    class Config:
        env_prefix = 'APP'

    @classmethod
    def load(cls):
        return load_settings(cls=cls, load_env=True)
