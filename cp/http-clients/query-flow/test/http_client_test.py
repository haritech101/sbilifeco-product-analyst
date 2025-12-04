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
from sbilifeco.boundaries.product_analyst.query_flow import BaseQueryFlow
from sbilifeco.cp.product_analyst.query_flow.http_server import QueryFlowHttpServer
from sbilifeco.cp.product_analyst.query_flow.http_client import QueryFlowHttpClient


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)

        # Initialise the service(s) here
        self.faker = Faker()

        if self.test_type == "unit":
            self.service = AsyncMock(spec=BaseQueryFlow)

            self.http_server = (
                QueryFlowHttpServer()
                .set_query_flow(self.service)
                .set_http_port(http_port)
            )
            await self.http_server.listen()

        # Initialise the client(s) here
        self.client = QueryFlowHttpClient()
        (
            self.client.set_proto("http")
            .set_host(staging_host if self.test_type == "staging" else "localhost")
            .set_port(http_port)
        )

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        if self.test_type == "unit":
            await self.http_server.stop()
        patch.stopall()

    async def test_query(self) -> None:
        # Arrange
        request_id = uuid4().hex
        query = self.faker.sentence()

        fn_request_search = patch.object(
            self.service,
            "request_search",
            AsyncMock(return_value=Response.ok(request_id)),
        ).start()
        fn_search = patch.object(
            self.service, "search", AsyncMock(return_value=Response.ok(None))
        ).start()

        # Act
        response = await self.client.request_search()

        # Assert
        self.assertTrue(response.is_success, response.message)
        fn_request_search.assert_called_once_with()
        assert response.payload is not None

        # Act
        response = await self.client.search(response.payload, query)

        # Assert
        self.assertTrue(response.is_success, response.message)
        fn_search.assert_called_once_with(request_id, query)
