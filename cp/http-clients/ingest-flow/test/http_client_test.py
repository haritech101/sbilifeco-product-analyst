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
from sbilifeco.boundaries.product_analyst.ingest_flow import (
    BaseIngestFlow,
    IDNameEntity,
    SortField,
    SortDirection,
)
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

    async def test_get_materials(self) -> None:
        # Arrange
        request_id = uuid4().hex
        page = 1
        page_size = 5
        sorts = {SortField.CREATED_AT: SortDirection.DESCENDING}
        materials = [
            IDNameEntity(
                id=uuid4().hex, name=name, created_at=self.faker.date_time_this_year()
            )
            for name in self.faker.words(page_size)
        ]

        fn_get_materials = patch.object(
            self.ingest_flow,
            "get_materials",
            return_value=Response.ok(materials),
        ).start()

        # Act
        response = await self.client.get_materials(page_size, page, sorts)

        # Assert
        self.assertTrue(response.is_success, response.message)

        fn_get_materials.assert_called_once()
        fn_args = fn_get_materials.call_args[0]
        self.assertEqual(fn_args[0], page_size)
        self.assertEqual(fn_args[1], page)
        self.assertEqual(fn_args[2], sorts)

        assert response.payload is not None
        self.assertEqual(response.payload, materials)
