import re
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
from datetime import datetime, date
from sbilifeco.models.base import Response

# Import the necessary service(s) here
from sbilifeco.models.vectorisation import RecordMetadata, VectorisedRecord
from sbilifeco.gateways.qdrant import QdrantGateway
from qdrant_client import AsyncQdrantClient


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)
        qdrant_url = getenv(EnvVars.qdrant_url, Defaults.qdrant_url)
        self.collection_name = getenv(EnvVars.collection_name, Defaults.collection_name)

        # Initialise the service(s) here
        self.faker = Faker()

        if self.test_type == "unit":
            self.service = QdrantGateway()
            self.service.set_url(qdrant_url).set_collection_name(self.collection_name)
            await self.service.async_init()

        # Initialise other tools here
        self.qdrant_client = AsyncQdrantClient(url=f"{qdrant_url}")

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        if self.test_type == "unit":
            await self.service.async_shutdown()
            if await self.qdrant_client.collection_exists(
                collection_name=self.collection_name
            ):
                await self.qdrant_client.delete_collection(
                    collection_name=self.collection_name
                )
            await self.qdrant_client.close()
        patch.stopall()

    async def test_vectorise(self) -> None:
        # Arrange
        request_id = uuid4().hex
        material = self.faker.paragraph()

        # Act
        response = await self.service.vectorise(request_id, material)

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None
        self.assertTrue(response.payload)

    async def test_create_read_delete(self) -> None:
        # Arrange
        source_id = uuid4().hex
        source = " ".join(self.faker.words(3))
        material = self.faker.paragraph()
        record_id = uuid4().hex
        vector = [float(randint(0, 100)) for _ in range(384)]

        record_in = VectorisedRecord(
            id=record_id,
            document=material,
            metadata=RecordMetadata(source_id=source_id, source=source),
            vector=vector,
        )

        # Act - Create/Update
        crupdate_response = await self.service.crupdate(record_in)

        # Assert - Create/Update
        self.assertTrue(crupdate_response.is_success, crupdate_response.message)

        # Act - Read
        read_response = await self.service.read_by_id(record_id)

        # Assert - Read
        self.assertTrue(read_response.is_success, read_response.message)

        record_out = read_response.payload
        assert record_out is not None

        record_in.vector = []
        self.assertEqual(record_out, record_in)

        # Act - Delete
        delete_response = await self.service.delete_by_id(record_id)

        # Assert - Delete
        self.assertTrue(delete_response.is_success, delete_response.message)

        # Act - Read
        read_response = await self.service.read_by_id(record_id)

        # Assert - Read
        self.assertFalse(read_response.is_success)
        self.assertEqual(read_response.code, 404)

    async def test_read_by_criteria(self) -> None:
        # Arrange
        source_id = uuid4().hex
        source = " ".join(self.faker.words(3))
        material = self.faker.paragraph()
        record_id = uuid4().hex
        vector = [float(randint(0, 100)) for _ in range(384)]

        record_in = VectorisedRecord(
            id=record_id,
            document=material,
            metadata=RecordMetadata(source_id=source_id, source=source),
            vector=vector,
        )

        # Act - Create/Update
        crupdate_response = await self.service.crupdate(record_in)

        # Assert - Create/Update
        self.assertTrue(crupdate_response.is_success, crupdate_response.message)

        # Act - Read by Criteria
        criteria = {"source_id": source_id}
        read_response = await self.service.read_by_criteria(criteria)

        # Assert - Read by Criteria
        self.assertTrue(read_response.is_success, read_response.message)
        records_out = read_response.payload
        assert records_out is not None
        self.assertTrue(records_out)
        record_out = records_out[0]
        record_in.vector = []
        self.assertEqual(record_out, record_in)

    async def test_delete_by_criteria(self) -> None:
        # Arrange
        source_id = uuid4().hex
        source = " ".join(self.faker.words(3))
        material = self.faker.paragraph()
        record_id = uuid4().hex
        vector = [float(randint(0, 100)) for _ in range(384)]

        record_in = VectorisedRecord(
            id=record_id,
            document=material,
            metadata=RecordMetadata(source_id=source_id, source=source),
            vector=vector,
        )

        # Act - Create/Update
        crupdate_response = await self.service.crupdate(record_in)

        # Assert - Create/Update
        self.assertTrue(crupdate_response.is_success, crupdate_response.message)

        # Act - Read
        read_response = await self.service.read_by_id(record_id)

        # Assert - Read
        self.assertTrue(read_response.is_success, read_response.message)

        record_out = read_response.payload
        assert record_out is not None

        record_in.vector = []
        self.assertEqual(record_out, record_in)

        # Act - Delete by Criteria
        criteria = {"source_id": source_id}
        delete_response = await self.service.delete_by_criteria(criteria)

        # Assert - Delete by Criteria
        self.assertTrue(delete_response.is_success, delete_response.message)

        # Act - Read by ID
        read_response = await self.service.read_by_id(record_id)

        # Assert - Read by ID
        self.assertFalse(read_response.is_success)
        self.assertEqual(read_response.code, 404)

    async def test_search_by_vector(self) -> None:
        # Arrange
        source_id = uuid4().hex
        source = " ".join(self.faker.words(3))
        material = self.faker.paragraph()
        record_id = uuid4().hex
        vector = [float(randint(0, 100)) for _ in range(384)]
        search_vector = vector.copy()
        for i in [randint(0, len(vector) - 1) for _ in range(4)]:
            search_vector[i] += 0.01  # Slightly modify to simulate a real search

        record_in = VectorisedRecord(
            id=record_id,
            document=material,
            metadata=RecordMetadata(source_id=source_id, source=source),
            vector=vector,
        )

        # Act - Create/Update
        crupdate_response = await self.service.crupdate(record_in)

        # Assert - Create/Update
        self.assertTrue(crupdate_response.is_success, crupdate_response.message)

        # Act - Search by Vector
        search_response = await self.service.search_by_vector(vector)

        # Assert - Search by Vector
        self.assertTrue(search_response.is_success, search_response.message)

        records_out = search_response.payload
        assert records_out is not None
        self.assertTrue(records_out)

        record_out = records_out[0]
        self.assertGreater(record_out.score, 0.0)

        record_out.score = 0.0
        record_in.vector = []
        self.assertEqual(record_out, record_in)
