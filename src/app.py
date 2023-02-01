from aiopg import connect
from aiopg.connection import Connection, Cursor

from settings import AppSettings


class Application:
    repository: Connection
    settings: AppSettings

    def __init__(self, settings: AppSettings):
        self.settings = settings

    def get_db_uri(self) -> str:
        settings = self.settings.repository
        return f"postgresql://{settings.user}:{settings.password}@{settings.host}:5432/{settings.database}"

    async def db_connect(self):
        self.repository = await connect(**self.settings.repository.dict())

    async def db_disconnect(self):
        await self.repository.close()

    async def db_get_cursor(self) -> Cursor:
        return await self.repository.cursor()

settings = AppSettings.load()
application = Application(settings)
