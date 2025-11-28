from asyncio import run, sleep
from dotenv import load_dotenv
from os import getenv
from envvars import EnvVars, Defaults
from sbilifeco.gateways.file_system_chromadb import FileSystemChromDB
from sbilifeco.cp.vectoriser.http_server import VectoriserHttpServer
from sbilifeco.cp.vector_repo.http_server import VectorRepoHttpServer


class ChromaDBGatewayMicroservice:
    async def run(self) -> None:
        db_path = getenv(EnvVars.db_path, Defaults.db_path)
        collection_name = getenv(EnvVars.collection_name, Defaults.collection_name)
        http_port_vectoriser = int(
            getenv(EnvVars.http_port_vectoriser, Defaults.http_port_vectoriser)
        )
        http_port_vector_repo = int(
            getenv(EnvVars.http_port_vector_repo, Defaults.http_port_vector_repo)
        )

        self.gateway = FileSystemChromDB()
        (self.gateway.set_db_path(db_path).set_collection_name(collection_name))
        await self.gateway.async_init()

        self.http_server_vectoriser = VectoriserHttpServer()
        (
            self.http_server_vectoriser.set_vectoriser(self.gateway).set_http_port(
                http_port_vectoriser
            )
        )
        await self.http_server_vectoriser.listen()

        self.http_server_vector_repo = VectorRepoHttpServer()
        (
            self.http_server_vector_repo.set_vector_repo(self.gateway).set_http_port(
                http_port_vector_repo
            )
        )
        await self.http_server_vector_repo.listen()

    async def run_forever(self) -> None:
        await self.run()
        while True:
            await sleep(5000)


if __name__ == "__main__":
    load_dotenv()
    run(ChromaDBGatewayMicroservice().run_forever())
