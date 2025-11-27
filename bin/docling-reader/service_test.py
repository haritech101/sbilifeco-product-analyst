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
from service import DoclingReaderMicroservice
from sbilifeco.cp.material_reader.http_client import MaterialReaderHttpClient
from pprint import pprint


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)

        # Initialise the service(s) here
        self.faker = Faker()

        if self.test_type == "unit":
            self.service = DoclingReaderMicroservice()
            await self.service.run()

        # Initialise the client(s) here
        self.client = MaterialReaderHttpClient()
        self.client.set_proto("http").set_host(
            staging_host if self.test_type == "staging" else "localhost"
        ).set_port(http_port)

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        # if self.test_type == "unit":
        #     await self.service.async_shutdown()
        patch.stopall()

    async def test_read_material(self) -> None:
        # Arrange
        material = b""
        with open(".local/brochure.pdf", "rb") as pdf_file:
            material = pdf_file.read()

        # Act
        ingest_response = await self.client.read_material(material)

        # Assert
        self.assertTrue(ingest_response.is_success, ingest_response.message)
        assert ingest_response.payload is not None
        material_id = ingest_response.payload

        # Act
        chunk_response = await self.client.read_next_chunk(material_id)

        # Assert
        self.assertTrue(chunk_response.is_success, chunk_response.message)
        assert chunk_response.payload is not None
        pprint(chunk_response.payload)
