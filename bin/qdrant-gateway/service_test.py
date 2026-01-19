import sys

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from dotenv import load_dotenv
from envvars import EnvVars, Defaults
from uuid import uuid4
from random import randint, random
from faker import Faker
from datetime import datetime, date
from sbilifeco.models.base import Response

# Import the necessary service(s) here
from pprint import pprint
from service import QdrantGatewayMicroservice
from sbilifeco.models.vectorisation import VectorisedRecord, RecordMetadata
from sbilifeco.cp.vectoriser.http_client import VectoriserHttpClient
from sbilifeco.cp.vector_repo.http_client import VectorRepoHttpClient
from qdrant_client import AsyncQdrantClient


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)
        vectoriser_http_port = int(
            getenv(EnvVars.vectoriser_http_port, Defaults.vectoriser_http_port)
        )
        vector_repo_http_port = int(
            getenv(EnvVars.vector_repo_http_port, Defaults.vector_repo_http_port)
        )
        self.collection_name = getenv(EnvVars.collection_name, Defaults.collection_name)
        self.qdrant_url = getenv(EnvVars.qdrant_url, Defaults.qdrant_url)

        # Initialise the service(s) here
        self.faker = Faker()

        if self.test_type == "unit":
            self.service = QdrantGatewayMicroservice()
            await self.service.run()

        # Initialise the client(s) here
        self.vectoriser_client = VectoriserHttpClient()
        (
            self.vectoriser_client.set_proto("http")
            .set_host(staging_host if self.test_type == "staging" else "localhost")
            .set_port(vectoriser_http_port)
        )

        self.vector_repo_client = VectorRepoHttpClient()
        (
            self.vector_repo_client.set_proto("http")
            .set_host(staging_host if self.test_type == "staging" else "localhost")
            .set_port(vector_repo_http_port)
        )

        self.qdrant_client = AsyncQdrantClient(url=self.qdrant_url)

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        if self.test_type == "unit":
            await self.qdrant_client.delete_collection(
                collection_name=self.collection_name
            )
            await self.qdrant_client.close()
        patch.stopall()

    async def test_vectorise(self) -> None:
        # Arrange
        request_id = uuid4().hex
        sentence = self.faker.sentence()

        # Act
        response = await self.vectoriser_client.vectorise(request_id, sentence)

        # Assert
        self.assertTrue(response.is_success, response.message)

        vector = response.payload
        assert vector is not None
        self.assertTrue(vector)

        pprint(vector[:10])

        tensor = vector[0]
        self.assertIsInstance(tensor, float)

    async def test_create_and_read_vector(self) -> None:
        # Arrange
        record = VectorisedRecord(
            id=uuid4().hex,
            document=self.faker.paragraph(),
            vector=[random() for _ in range(384)],
            metadata=RecordMetadata(
                source_id=uuid4().hex,
                source=self.faker.street_name(),
            ),
        )

        # Act - Create
        create_response = await self.vector_repo_client.crupdate(record)

        # Assert - Create
        self.assertTrue(create_response.is_success, create_response.message)

        # Act - Read
        read_response = await self.vector_repo_client.read_by_id(record.id)

        # Assert - Read
        self.assertTrue(read_response.is_success, read_response.message)

        retrieved_record = read_response.payload
        assert retrieved_record is not None

        pprint(retrieved_record)

        record.vector = []
        self.assertEqual(retrieved_record, record)
