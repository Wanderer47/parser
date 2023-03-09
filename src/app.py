from aiopg.sa import create_engine
from aiopg.sa import Engine, SAConnection


from settings import RepositorySettings


class Application:
    engine: Engine
    settings: RepositorySettings

    def __init__(self, settings: RepositorySettings):
        self.settings = settings

    def get_db_uri(self) -> str:
        settings = self.settings
        return f"postgresql://{settings.user}:{settings.password}@{settings.host}:5432/{settings.database}"

    async def db_engine(self):
        self.engine = await create_engine(
                user=self.settings.user,
                database=self.settings.database,
                host=self.settings.host,
                password=self.settings.password)

    async def db_disconnect(self):
        self.engine.close()

    async def db_get_connect(self):
        return self.engine.acquire()
        #async with self.engine:
        #    async with self.engine.acquire() as conn:
        #        return conn

settings = RepositorySettings()
application = Application(settings)

