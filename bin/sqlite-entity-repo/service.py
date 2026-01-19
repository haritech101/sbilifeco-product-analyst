from __future__ import annotations
from asyncio import sleep, run
from dotenv import load_dotenv
from os import getenv

from sbilifeco.gateways.sqlite_entity_repo import SQLiteEntityRepo
from sbilifeco.cp.id_name_repo.http_server import IDNameRepoHttpServer
from envvars import EnvVars, Defaults


class SQLiteEntityRepoMicroservice:
    async def run(self) -> None:
        # Env vars
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        db_path = getenv(EnvVars.db_path, "")

        # Services
        self.repo = SQLiteEntityRepo().set_path(db_path)
        await self.repo.async_init()

        self.http_server = IDNameRepoHttpServer()
        (self.http_server.set_id_name_repo(self.repo).set_http_port(http_port))
        await self.http_server.listen()

    async def run_forever(self) -> None:
        await self.run()
        while True:
            await sleep(5000)


if __name__ == "__main__":
    load_dotenv()
    run(SQLiteEntityRepoMicroservice().run_forever())
