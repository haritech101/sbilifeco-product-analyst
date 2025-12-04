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
from service import QueryFlowMicroservice
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
            self.service = QueryFlowMicroservice()
            await self.service.run()

        # Initialise the client(s) here
        self.client = QueryFlowHttpClient()
        (
            self.client.set_proto("http")
            .set_host(staging_host if self.test_type == "staging" else "localhost")
            .set_port(http_port)
        )

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        # if self.test_type == "unit":
        #     await self.service.async_shutdown()
        patch.stopall()

    async def test_search(self) -> None:
        # Arrange
        query = "What is the premium for a 35-year old?"

        # Act
        response = await self.client.request_search()

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None
        request_id = response.payload

        # Act
        response = await self.client.search(request_id, query)

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None
