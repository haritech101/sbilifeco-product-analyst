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
from datetime import datetime, date
from sbilifeco.models.base import Response

# Import the necessary service(s) here
from service import SQLiteEntityRepoMicroservice
from sbilifeco.cp.id_name_repo.http_client import IDNameRepoHttpClient
from sbilifeco.boundaries.id_name_repo import IDNameEntity


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)

        # Initialise the service(s) here
        self.faker = Faker()

        if self.test_type == "unit":
            self.service = SQLiteEntityRepoMicroservice()
            await self.service.run()

        # Initialise the client(s) here
        self.client = IDNameRepoHttpClient()
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

    async def test_crud(self) -> None:
        # Arrange
        create_request_id = uuid4().hex
        read_request_id = uuid4().hex
        delete_request_id = uuid4().hex
        entity = IDNameEntity(
            id=uuid4().hex,
            name=self.faker.name(),
            created_at=datetime.now(),
            others={self.faker.word(): self.faker.sentence()},
        )

        ## Create
        # Act
        create_response = await self.client.crupdate(create_request_id, entity)

        # Assert
        self.assertTrue(create_response.is_success, create_response.message)

        ## Read
        # Act
        read_response = await self.client.read_by_id(read_request_id, entity.id)

        # Assert
        self.assertTrue(read_response.is_success, read_response.message)
        assert read_response.payload is not None
        self.assertEqual(read_response.payload, entity)

        ## Delete
        # Act
        delete_response = await self.client.delete_by_id(delete_request_id, entity.id)

        # Assert
        self.assertTrue(delete_response.is_success, delete_response.message)

        ## Read
        # Act
        read_response = await self.client.read_by_id(read_request_id, entity.id)

        # Assert
        self.assertFalse(read_response.is_success, read_response.message)
        self.assertEqual(read_response.code, 404)
