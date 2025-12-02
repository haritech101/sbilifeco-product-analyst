import sys

from service import ChromaDBGatewayMicroservice

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
from shutil import rmtree

# Import the necessary service(s) here
from sbilifeco.models.vectorisation import VectorisedRecord, RecordMetadata
from sbilifeco.cp.vectoriser.http_client import VectoriserHttpClient
from sbilifeco.cp.vector_repo.http_client import VectorRepoHttpClient


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port_vectoriser = int(
            getenv(EnvVars.http_port_vectoriser, Defaults.http_port_vectoriser)
        )
        http_port_vector_repo = int(
            getenv(EnvVars.http_port_vector_repo, Defaults.http_port_vector_repo)
        )
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)
        self.db_path = getenv(EnvVars.db_path, Defaults.db_path)

        # Initialise the service(s) here
        self.faker = Faker()

        if self.test_type == "unit":
            self.service = ChromaDBGatewayMicroservice()
            await self.service.run()

        # Initialise the client(s) here
        self.client_vectoriser = VectoriserHttpClient()
        (
            self.client_vectoriser.set_proto("http")
            .set_host(staging_host if self.test_type == "staging" else "localhost")
            .set_port(http_port_vectoriser)
        )
        self.client_vector_repo = VectorRepoHttpClient()
        (
            self.client_vector_repo.set_proto("http")
            .set_host(staging_host if self.test_type == "staging" else "localhost")
            .set_port(http_port_vector_repo)
        )

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        if self.test_type == "unit":
            rmtree(self.db_path)
        #     await self.service.async_shutdown()
        patch.stopall()

    async def test_vectorise(self) -> None:
        # Arrange
        request_id = uuid4().hex
        material = self.faker.sentence()

        # Act
        response = await self.client_vectoriser.vectorise(request_id, material)

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None
        self.assertNotEqual(response.payload[0], 0)

    async def test_store_and_retrieve(self) -> None:
        # Arrange
        document = self.faker.sentence()
        vector = [randint(0, 255) for _ in range(32)]
        metadata = RecordMetadata(
            source_id=uuid4().hex, source=self.faker.name(), chunk_num=1
        )
        record = VectorisedRecord(
            id=uuid4().hex, document=document, vector=vector, metadata=metadata
        )

        # Act
        crupdate_response = await self.client_vector_repo.crupdate(record)

        # Assert
        self.assertTrue(crupdate_response.is_success, crupdate_response.message)

        # Arrange
        record.vector = []

        # Act
        read_response = await self.client_vector_repo.read_by_id(record.id)

        # Assert
        self.assertTrue(read_response.is_success, read_response.message)
        assert read_response.payload is not None
        self.assertEqual(read_response.payload, record)
