from asyncio import sleep, run
from dotenv import load_dotenv
from os import getenv

from envvars import EnvVars, Defaults
from sbilifeco.flows.product_analyst.query_flow import QueryFlow
from sbilifeco.cp.product_analyst.query_flow.http_server import QueryFlowHttpServer
from sbilifeco.cp.llm.http_client import LLMHttpClient
from sbilifeco.cp.vectoriser.http_client import VectoriserHttpClient
from sbilifeco.cp.vector_repo.http_client import VectorRepoHttpClient


class QueryFlowMicroservice:
    async def run(self) -> None:
        # Env vars
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        llm_proto = getenv(EnvVars.llm_proto, Defaults.llm_proto)
        llm_host = getenv(EnvVars.llm_host, Defaults.llm_host)
        llm_port = int(getenv(EnvVars.llm_port, Defaults.llm_port))
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

        # Services
        llm_client = LLMHttpClient()
        (llm_client.set_proto(llm_proto).set_host(llm_host).set_port(llm_port))

        vectoriser_client = VectoriserHttpClient()
        (
            vectoriser_client.set_proto(vectoriser_proto)
            .set_host(vectoriser_host)
            .set_port(vectoriser_port)
        )

        vector_repo_client = VectorRepoHttpClient()
        (
            vector_repo_client.set_proto(vector_repo_proto)
            .set_host(vector_repo_host)
            .set_port(vector_repo_port)
        )

        self.query_flow = QueryFlow()
        (
            self.query_flow.set_llm(llm_client)
            .set_vectoriser(vectoriser_client)
            .set_vector_repo(vector_repo_client)
        )
        await self.query_flow.async_init()

        self.http_server = QueryFlowHttpServer()
        (self.http_server.set_query_flow(self.query_flow).set_http_port(http_port))
        await self.http_server.listen()

    async def run_forever(self) -> None:
        await self.run()
        while True:
            await sleep(5000)


if __name__ == "__main__":
    load_dotenv()
    run(QueryFlowMicroservice().run_forever())
