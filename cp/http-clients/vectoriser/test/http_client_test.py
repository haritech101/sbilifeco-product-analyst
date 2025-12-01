import sys
from typing import cast

sys.path.append("./src")

from os import getenv
from random import randint
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch

# Import the necessary service(s) here
from uuid import uuid4

from dotenv import load_dotenv
from envvars import Defaults, EnvVars
from faker import Faker
from sbilifeco.models.base import Response
from sbilifeco.boundaries.vectoriser import BaseVectoriser
from sbilifeco.cp.vectoriser.http_server import VectoriserHttpServer

from sbilifeco.cp.vectoriser.http_client import VectoriserHttpClient


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))

        # Initialise the service(s) here
        self.faker = Faker()
        self.vectoriser: BaseVectoriser = AsyncMock()

        self.service = VectoriserHttpServer()
        self.service.set_vectoriser(self.vectoriser).set_http_port(http_port)
        await self.service.listen()

        # Initialise the client(s) here
        self.client = VectoriserHttpClient()
        self.client.set_proto("http").set_host("localhost").set_port(http_port)

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        await self.service.stop()
        patch.stopall()

    async def test_vectorise(self) -> None:
        # Arrange
        request_id = uuid4().hex
        material = self.faker.text()
        vectorise = patch.object(
            self.vectoriser, "vectorise", return_value=Response.ok([])
        ).start()

        # Act
        response = await self.client.vectorise(request_id, material)

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None

        vectorise.assert_called_once_with(request_id, material)
