import sys

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase
from dotenv import load_dotenv
from envvars import EnvVars, Defaults
from uuid import uuid4

# Import the necessary service(s) here
from sbilifeco.gateways.file_system_chromadb import FileSystemChromDB
from sbilifeco.models.vectorisation import VectorisedRecord, RecordMetadata
from random import randint
from shutil import rmtree
from faker import Faker


class FileSystemChromaDBTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()
        self.db_path = getenv(EnvVars.db_path, Defaults.db_path)
        self.collection_name = getenv(EnvVars.collection_name, "")

        # Initialise the service(s)
        self.service = FileSystemChromDB()
        self.service.set_db_path(self.db_path).set_collection_name(self.collection_name)
        await self.service.async_init()
        ...

        # Initialise the client(s) here
        ...

        self.faker = Faker()

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        await self.service.async_shutdown()
        rmtree(self.db_path, ignore_errors=True)

    async def test_vectorise(self) -> None:
        # Arrange
        hello = "Hello, World!"
        request_id = uuid4().hex

        # Act
        vectorise_response = await self.service.vectorise(request_id, hello)

        # Assert
        self.assertTrue(vectorise_response.is_success, vectorise_response.message)
        assert vectorise_response.payload is not None

        self.assertTrue(vectorise_response.payload)
        self.assertNotEqual(0, vectorise_response.payload[0])
        ...

    async def test_create(self) -> None:
        # Arrange
        id = uuid4().hex
        source_id = uuid4().hex
        record = VectorisedRecord(
            id=id,
            vector=[randint(0, 100) for _ in range(256)],
            document=self.faker.paragraph(),
            metadata=RecordMetadata(
                source_id=source_id, source=" ".join(self.faker.words(3)), chunk_num=0
            ),
        )

        # Act
        create_response = await self.service.crupdate(record)

        # Assert
        self.assertTrue(create_response.is_success, create_response.message)

        read_response = await self.service.read_by_id(id)
        self.assertTrue(read_response.is_success, read_response.message)
        assert read_response.payload is not None

        # Fetched data won't have the vector, so remove it for comparison
        record.vector = []
        self.assertEqual(record, read_response.payload)
        ...

    async def test_update(self) -> None:
        # Arrange
        id = uuid4().hex
        source_id = uuid4().hex
        record = VectorisedRecord(
            id=id,
            vector=[randint(0, 100) for _ in range(256)],
            document=self.faker.paragraph(),
            metadata=RecordMetadata(
                source_id=source_id, source=" ".join(self.faker.words(3)), chunk_num=0
            ),
        )
        await self.service.crupdate(record)

        record.document = self.faker.paragraph()
        record.vector = [randint(0, 100) for _ in range(256)]

        # Act
        update_response = await self.service.crupdate(record)

        # Assert
        self.assertTrue(update_response.is_success, update_response.message)

        read_response = await self.service.read_by_id(id)
        self.assertTrue(read_response.is_success, read_response.message)
        assert read_response.payload is not None

        # Fetched data won't have the vector, so remove it for comparison
        record.vector = []
        self.assertEqual(record, read_response.payload)
        ...

    async def test_delete_by_id(self) -> None:
        # Arrange
        id = uuid4().hex
        source_id = uuid4().hex
        record = VectorisedRecord(
            id=id,
            vector=[randint(0, 100) for _ in range(256)],
            document=self.faker.paragraph(),
            metadata=RecordMetadata(
                source_id=source_id, source=" ".join(self.faker.words(3)), chunk_num=0
            ),
        )
        await self.service.crupdate(record)

        read_response = await self.service.read_by_id(id)
        self.assertTrue(read_response.is_success, read_response.message)
        assert read_response.payload is not None

        # Act
        delete_response = await self.service.delete_by_id(id)

        # Assert
        self.assertTrue(delete_response.is_success, delete_response.message)

        read_response = await self.service.read_by_id(id)
        self.assertFalse(read_response.is_success, read_response.message)
        self.assertEqual(404, read_response.code)
        ...

    async def test_delete_by_criteria(self) -> None:
        # Arrange
        id = uuid4().hex
        source_id = uuid4().hex
        record = VectorisedRecord(
            id=id,
            vector=[randint(0, 100) for _ in range(256)],
            document=self.faker.paragraph(),
            metadata=RecordMetadata(
                source_id=source_id, source=" ".join(self.faker.words(3)), chunk_num=0
            ),
        )
        await self.service.crupdate(record)

        read_response = await self.service.read_by_id(id)
        self.assertTrue(read_response.is_success, read_response.message)
        assert read_response.payload is not None

        # Act
        delete_response = await self.service.delete_by_criteria(
            {"source": record.metadata.source}
        )

        # Assert
        self.assertTrue(delete_response.is_success, delete_response.message)

        read_response = await self.service.read_by_id(id)
        self.assertFalse(read_response.is_success, read_response.message)
        self.assertEqual(404, read_response.code)
        ...

    async def test_read_by_id(self) -> None:
        # Arrange
        id = uuid4().hex
        source_id = uuid4().hex
        record = VectorisedRecord(
            id=id,
            vector=[randint(0, 100) for _ in range(256)],
            document=self.faker.paragraph(),
            metadata=RecordMetadata(
                source_id=source_id, source=" ".join(self.faker.words(3)), chunk_num=0
            ),
        )
        await self.service.crupdate(record)

        # Act
        read_response = await self.service.read_by_id(id)

        # Assert
        self.assertTrue(read_response.is_success, read_response.message)
        assert read_response.payload is not None

        # Fetched data won't have the vector, so remove it for comparison
        record.vector = []
        self.assertEqual(record, read_response.payload)
        ...

    async def test_read_by_criteria(self) -> None:
        # Arrange
        id = uuid4().hex
        source_id = uuid4().hex
        record = VectorisedRecord(
            id=id,
            vector=[randint(0, 100) for _ in range(256)],
            document=self.faker.paragraph(),
            metadata=RecordMetadata(
                source_id=source_id, source=" ".join(self.faker.words(3)), chunk_num=0
            ),
        )
        await self.service.crupdate(record)

        # Act
        read_response = await self.service.read_by_criteria(
            {"source_id": record.metadata.source_id if record.metadata else None}
        )

        # Assert
        self.assertTrue(read_response.is_success, read_response.message)
        assert read_response.payload is not None

        # Fetched data won't have the vector, so remove it for comparison
        record.vector = []
        self.assertEqual(record, read_response.payload[0])
        ...

    async def test_search_by_vector(self) -> None:
        # Arrange
        id = uuid4().hex
        source_id = uuid4().hex
        record = VectorisedRecord(
            id=id,
            vector=[randint(0, 100) for _ in range(256)],
            document=self.faker.paragraph(),
            metadata=RecordMetadata(
                source_id=source_id, source=" ".join(self.faker.words(3)), chunk_num=0
            ),
        )
        await self.service.crupdate(record)

        # Act
        search_vector = record.vector.copy()[:240]
        search_vector.extend([0] * 16)  # Pad to match vector size

        read_response = await self.service.search_by_vector(
            search_vector, num_results=5
        )

        # Assert
        self.assertTrue(read_response.is_success, read_response.message)
        assert read_response.payload is not None

        list_of_records = read_response.payload
        self.assertTrue(list_of_records)
        self.assertEqual(len(list_of_records), 1)

        fetched_record = list_of_records[0]

        record.vector = (
            []
        )  # Fetched data won't have the vector, so remove it for comparison
        fetched_record.score = 0.0  # Ignore score for equality check
        self.assertEqual(fetched_record, record)
        ...
