from os import getenv
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from dotenv import load_dotenv
from envvars import EnvVars, Defaults
from uuid import uuid4
from random import randint
from faker import Faker
from sbilifeco.models.base import Response
from shutil import rmtree

# Import the necessary service(s) here
from sbilifeco.cp.product_analyst.ingest_flow.http_client import IngestFlowHttpClient
from sbilifeco.cp.vector_repo.http_client import VectorRepoHttpClient
from service import IngestFlowMicroservice


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)
        vector_repo_proto = getenv(
            EnvVars.vector_repo_proto, Defaults.vector_repo_proto
        )
        vector_repo_host = getenv(EnvVars.vector_repo_host, Defaults.vector_repo_host)
        vector_repo_port = int(
            getenv(EnvVars.vector_repo_port, Defaults.vector_repo_port)
        )

        # Initialise the service(s) here
        self.faker = Faker()

        if self.test_type == "unit":
            self.service = IngestFlowMicroservice()
            await self.service.run()

        # Initialise the client(s) here
        self.client = IngestFlowHttpClient()
        (
            self.client.set_proto("http")
            .set_host(staging_host if self.test_type == "staging" else "localhost")
            .set_port(http_port)
        )

        self.vector_repo_client = VectorRepoHttpClient()
        (
            self.vector_repo_client.set_proto(vector_repo_proto)
            .set_host(vector_repo_host)
            .set_port(vector_repo_port)
        )

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        # if self.test_type == "unit":
        #     await self.service.async_shutdown()
        patch.stopall()
        try:
            await self.vector_repo_client.delete_by_criteria({"source": self.title})
        except Exception:
            ...

    async def test_ingest(self) -> None:
        # Arrange
        self.title = self.faker.sentence()
        material = b""
        with open(".local/brochure.pdf", "rb") as pdf_file:
            material = pdf_file.read()

        # Act
        response = await self.client.request_ingestion()

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None
        request_id = response.payload

        # Act
        response = await self.client.ingest(request_id, self.title, material)

        # Assert
        self.assertTrue(response.is_success, response.message)

        # Assert
        read_response = await self.vector_repo_client.read_by_criteria(
            {"source": self.title}
        )

        self.assertTrue(read_response.is_success, read_response.message)
        assert read_response.payload is not None
