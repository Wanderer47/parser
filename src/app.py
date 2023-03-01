from aiopg.sa import create_engine
from aiopg.sa import Engine, SAConnection


from settings import AppSettings


class Application:
    repository: Engine
    settings: AppSettings

    def __init__(self, settings: AppSettings):
        self.settings = settings

    def get_db_uri(self) -> str:
        settings = self.settings.repository
        return f"postgresql://{settings.user}:{settings.password}@{settings.host}:5432/{settings.database}"

    async def db_engine(self):
        async with create_engine(**self.settings.repository.dict()) as engine:
            self.repository = engine

    async def db_disconnect(self):
        await self.repository.wait_closed()

    async def db_get_connect(self) -> SAConnection:
        async with self.repository.acquire() as conn:
            return conn

settings = AppSettings()
application = Application(settings)
