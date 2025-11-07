import sys
import uuid

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
from sbilifeco.cp.material_reader.http_client import MaterialReaderHttpClient
from sbilifeco.cp.material_reader.http_server import MaterialReaderHttpServer
from sbilifeco.boundaries.material_reader import BaseMaterialReader


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))

        # Initialise the service(s) here
        self.faker = Faker()

        self.material_reader: BaseMaterialReader = AsyncMock()

        self.service = MaterialReaderHttpServer()
        self.service.set_material_reader(self.material_reader).set_http_port(http_port)
        await self.service.listen()

        # Initialise the client(s) here
        self.client = MaterialReaderHttpClient()
        self.client.set_proto("http").set_host("localhost").set_port(http_port)

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        await self.service.stop()
        patch.stopall()

    async def test_read_material(self) -> None:
        # Arrange
        material = self.faker.text()
        read_material = patch.object(
            self.material_reader, "read_material", return_value=Response.ok(uuid4().hex)
        ).start()

        # Act
        response = await self.client.read_material(material)

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None

        read_material.assert_called_once_with(material)

    async def test_read_next_chunk(self) -> None:
        # Arrange
        material_id = uuid4().hex
        read_next_chunk = patch.object(
            self.material_reader,
            "read_next_chunk",
            return_value=Response.ok(bytearray(self.faker.text(), "utf-8")),
        ).start()

        # Act
        response = await self.client.read_next_chunk(material_id)

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None
