from asyncio import run, sleep
from typing import NoReturn
from dotenv import load_dotenv
from os import getenv
from envvars import EnvVars, Defaults

# import required modules here
from sbilifeco.gateways.qdrant import QdrantGateway
from sbilifeco.cp.vector_repo.http_server import VectorRepoHttpServer
from sbilifeco.cp.vectoriser.http_server import VectoriserHttpServer


class QdrantGatewayMicroservice:
    async def run(self) -> None:
        # env
        qdrant_url = getenv(EnvVars.qdrant_url, Defaults.qdrant_url)
        collection_name = getenv(EnvVars.collection_name, Defaults.collection_name)
        vectoriser_http_server = int(
            getenv(EnvVars.vectoriser_http_port, Defaults.vectoriser_http_port)
        )
        vector_repo_http_server = int(
            getenv(EnvVars.vector_repo_http_port, Defaults.vector_repo_http_port)
        )

        # gateways
        qdrant_gateway = QdrantGateway()
        qdrant_gateway.set_url(qdrant_url).set_collection_name(collection_name)

        # http service
        vectoriser_http_server = (
            VectoriserHttpServer()
            .set_vectoriser(qdrant_gateway)
            .set_http_port(vectoriser_http_server)
        )

        vector_repo_http_server = (
            VectorRepoHttpServer()
            .set_vector_repo(qdrant_gateway)
            .set_http_port(vector_repo_http_server)
        )

        # initialise
        await qdrant_gateway.async_init()
        await vectoriser_http_server.listen()
        await vector_repo_http_server.listen()

    async def run_forever(self) -> NoReturn:
        await self.run()
        while True:
            await sleep(3600)


if __name__ == "__main__":
    load_dotenv()
    run(QdrantGatewayMicroservice().run_forever())
