import sys

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from dotenv import load_dotenv
from envvars import EnvVars, Defaults
from uuid import uuid4
from random import randint
from faker import Faker
from sbilifeco.models.base import Response

# Import the necessary service(s) here
from sbilifeco.boundaries.product_analyst.ingest_flow import BaseIngestFlow
from sbilifeco.cp.product_analyst.ingest_flow.http_server import IngestFlowHttpServer
from sbilifeco.cp.product_analyst.ingest_flow.http_client import IngestFlowHttpClient


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))

        # Initialise the service(s) here
        self.faker = Faker()

        self.ingest_flow: BaseIngestFlow = AsyncMock(spec=BaseIngestFlow)

        self.service = IngestFlowHttpServer()
        self.service.set_ingest_flow(self.ingest_flow).set_http_port(http_port)
        await self.service.listen()

        # Initialise the client(s) here
        self.client = IngestFlowHttpClient()
        self.client.set_proto("http").set_host("localhost").set_port(http_port)

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        await self.service.stop()
        patch.stopall()

    async def test_request_ingest(self) -> None:
        # Arrange
        request_ingestion = patch.object(
            self.ingest_flow, "request_ingestion", return_value=Response.ok(uuid4().hex)
        ).start()

        # Act
        response = await self.client.request_ingestion()

        # Assert
        self.assertTrue(response.is_success, response.message)

        request_ingestion.assert_called_once_with()

    async def test_ingest(self) -> None:
        # Arrange
        request_id = uuid4().hex
        title = " ".join(self.faker.words(4))
        material = self.faker.paragraph()
        ingest = patch.object(self.ingest_flow, "ingest").start()

        # Act
        response = await self.client.ingest(request_id, title, material)

        # Assert
        self.assertTrue(response.is_success, response.message)

        ingest.assert_called_once_with(request_id, title, material)
