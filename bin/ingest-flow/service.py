from asyncio import run, sleep
from dotenv import load_dotenv
from os import getenv
from envvars import EnvVars, Defaults

from sbilifeco.flows.product_analyst.ingest_flow import IngestFlow
from sbilifeco.cp.product_analyst.ingest_flow.http_server import IngestFlowHttpServer
from sbilifeco.cp.material_reader.http_client import MaterialReaderHttpClient
from sbilifeco.cp.vectoriser.http_client import VectoriserHttpClient
from sbilifeco.cp.vector_repo.http_client import VectorRepoHttpClient
from sbilifeco.cp.id_name_repo.http_client import IDNameRepoHttpClient


class IngestFlowMicroservice:
    async def run(self) -> None:
        # Env vars
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        material_reader_proto = getenv(
            EnvVars.material_reader_proto, Defaults.material_reader_proto
        )
        material_reader_host = getenv(
            EnvVars.material_reader_host, Defaults.material_reader_host
        )
        material_reader_port = int(
            getenv(EnvVars.material_reader_port, Defaults.material_reader_port)
        )
        vectoriser_proto = getenv(EnvVars.vectoriser_proto, Defaults.vectoriser_proto)
        vectoriser_host = getenv(EnvVars.vectoriser_host, Defaults.vectoriser_host)
        vectoriser_port = int(getenv(EnvVars.vectoriser_port, Defaults.vectoriser_port))
        vector_repo_proto = getenv(
            EnvVars.vector_repo_proto, Defaults.vector_repo_proto
        )
        vector_repo_host = getenv(EnvVars.vector_repo_host, Defaults.vector_repo_host)
        vector_repo_port = int(
            getenv(EnvVars.vector_repo_port, Defaults.vector_repo_port)
        )
        id_name_repo_proto = getenv(
            EnvVars.id_name_repo_proto, Defaults.id_name_repo_proto
        )
        id_name_repo_host = getenv(
            EnvVars.id_name_repo_host, Defaults.id_name_repo_host
        )
        id_name_repo_port = int(
            getenv(EnvVars.id_name_repo_port, Defaults.id_name_repo_port)
        )

        # Gateways and flows
        self.material_reader = MaterialReaderHttpClient()
        (
            self.material_reader.set_proto(material_reader_proto)
            .set_host(material_reader_host)
            .set_port(material_reader_port)
        )

        self.vectoriser = VectoriserHttpClient()
        (
            self.vectoriser.set_proto(vectoriser_proto)
            .set_host(vectoriser_host)
            .set_port(vectoriser_port)
        )

        self.vector_repo = VectorRepoHttpClient()
        (
            self.vector_repo.set_proto(vector_repo_proto)
            .set_host(vector_repo_host)
            .set_port(vector_repo_port)
        )

        self.id_name_repo = IDNameRepoHttpClient()
        (
            self.id_name_repo.set_proto(id_name_repo_proto)
            .set_host(id_name_repo_host)
            .set_port(id_name_repo_port)
        )

        self.ingest_flow = IngestFlow()
        (
            self.ingest_flow.set_material_reader(self.material_reader)
            .set_vectoriser(self.vectoriser)
            .set_vector_repo(self.vector_repo)
            .set_id_name_repo(self.id_name_repo)
        )
        await self.ingest_flow.async_init()

        # Controllers and presenters
        self.http_server = IngestFlowHttpServer()
        (self.http_server.set_ingest_flow(self.ingest_flow).set_http_port(http_port))
        await self.http_server.listen()

    async def run_forever(self) -> None:
        await self.run()
        while True:
            await sleep(5000)


if __name__ == "__main__":
    load_dotenv()
    run(IngestFlowMicroservice().run_forever())
