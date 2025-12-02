import sys

sys.path.append("./src")

from os import getenv
from random import randint
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from dotenv import load_dotenv
from envvars import Defaults, EnvVars
from faker import Faker
from sbilifeco.boundaries.vector_repo import BaseVectorRepo

# Import the necessary service(s) here
from sbilifeco.cp.vector_repo.http_server import VectorRepoHttpServer
from sbilifeco.models.base import Response
from sbilifeco.models.vectorisation import RecordMetadata, VectorisedRecord

from sbilifeco.cp.vector_repo.http_client import VectorRepoHttpClient


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))

        # Initialise the service(s) here
        self.faker = Faker()

        self.vector_repo: BaseVectorRepo = AsyncMock()

        self.service = VectorRepoHttpServer()
        self.service.set_vector_repo(self.vector_repo).set_http_port(http_port)
        await self.service.listen()

        # Initialise the client(s) here
        self.client = VectorRepoHttpClient()
        self.client.set_proto("http").set_host("localhost").set_port(http_port)

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        await self.service.stop()
        patch.stopall()

    async def test_crupdate(self) -> None:
        # Arrange
        record = VectorisedRecord(
            id=uuid4().hex,
            document=self.faker.paragraph(),
            vector=[randint(0, 100) for _ in range(256)],
            metadata=RecordMetadata(
                source_id=uuid4().hex, source=" ".join(self.faker.words(4))
            ),
        )
        crupdate = patch.object(
            self.vector_repo, "crupdate", return_value=Response.ok(None)
        ).start()

        # Act
        response = await self.client.crupdate(record)

        # Assert
        self.assertTrue(response.is_success, response.message)

        crupdate.assert_called_once_with(record)

    async def test_delete_by_id(self) -> None:
        # Arrange
        id = uuid4().hex
        delete_by_id = patch.object(
            self.vector_repo, "delete_by_id", return_value=Response.ok(None)
        ).start()

        # Act
        response = await self.client.delete_by_id(id)

        # Assert
        self.assertTrue(response.is_success, response.message)

        delete_by_id.assert_called_once_with(id)

    async def test_delete_by_criteria(self) -> None:
        # Arrange
        criteria = {"source": " ".join(self.faker.words(3))}
        delete_by_criteria = patch.object(
            self.vector_repo, "delete_by_criteria", return_value=Response.ok(None)
        ).start()

        # Act
        response = await self.client.delete_by_criteria(criteria)

        # Assert
        self.assertTrue(response.is_success, response.message)

        delete_by_criteria.assert_called_once_with(criteria)

    async def test_read_by_id(self) -> None:
        # Arrange
        id = uuid4().hex
        read_by_id = patch.object(
            self.vector_repo, "read_by_id", return_value=Response.ok(None)
        ).start()

        # Act
        response = await self.client.read_by_id(id)

        # Assert
        self.assertTrue(response.is_success, response.message)

        read_by_id.assert_called_once_with(id)

    async def test_read_by_criteria(self) -> None:
        # Arrange
        criteria = {"source": " ".join(self.faker.words(3))}
        read_by_criteria = patch.object(
            self.vector_repo, "read_by_criteria", return_value=Response.ok(None)
        ).start()

        # Act
        response = await self.client.read_by_criteria(criteria)

        # Assert
        self.assertTrue(response.is_success, response.message)

        read_by_criteria.assert_called_once_with(criteria)

    async def test_search_by_vector(self) -> None:
        # Arrange
        vector = [float(randint(0, 255)) for _ in range(256)]
        search_by_vector = patch.object(
            self.vector_repo, "search_by_vector", return_value=Response.ok(None)
        ).start()

        # Act
        response = await self.client.search_by_vector(vector)

        # Assert
        self.assertTrue(response.is_success, response.message)

        search_by_vector.assert_called_once_with(vector)
