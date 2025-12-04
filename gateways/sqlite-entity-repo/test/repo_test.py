import sys
import uuid

sys.path.append("./src")

from os import getenv, unlink
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from dotenv import load_dotenv
from envvars import EnvVars, Defaults
from uuid import uuid4
from random import randint
from faker import Faker
from sbilifeco.models.base import Response

# Import the necessary service(s) here
from datetime import datetime
from sbilifeco.gateways.sqlite_entity_repo import SQLiteEntityRepo, IDNameEntity


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)
        self.db_path = getenv(EnvVars.db_path, "")

        # Initialise the service(s) here
        self.faker = Faker()

        if self.test_type == "unit":
            self.service = SQLiteEntityRepo()
            (self.service.set_path(self.db_path))
            await self.service.async_init()

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        if self.test_type == "unit":
            await self.service.async_shutdown()
        patch.stopall()
        unlink(self.db_path)

    async def test_create_and_retrieve(self) -> None:
        # Arrange
        create_request_id = uuid4().hex
        read_request_id = uuid4().hex
        entity = IDNameEntity(
            id=uuid4().hex,
            name=self.faker.name(),
            created_at=datetime.now(),
            others={self.faker.word(): self.faker.sentence()},
        )

        # Act
        response = await self.service.crupdate(create_request_id, entity)

        # Assert
        self.assertTrue(response.is_success, response.message)

        # Act
        response = await self.service.read_by_id(read_request_id, entity.id)

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None
        self.assertEqual(entity, response.payload)

    async def test_create_and_update(self) -> None:
        # Arrange
        create_request_id = uuid4().hex
        update_request_id = uuid4().hex
        read_request_id = uuid4().hex
        entity = IDNameEntity(
            id=uuid4().hex,
            name=self.faker.name(),
            created_at=datetime.now(),
            others={self.faker.word(): self.faker.sentence()},
        )
        response = await self.service.crupdate(create_request_id, entity)
        assert response.is_success

        entity.name = self.faker.name()

        # Act
        response = await self.service.crupdate(update_request_id, entity)

        # Assert
        self.assertTrue(response.is_success, response.message)

        # Act
        response = await self.service.read_by_id(read_request_id, entity.id)

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None
        self.assertEqual(entity, response.payload)

    async def test_delete(self) -> None:
        # Arrange
        create_request_id = uuid4().hex
        delete_request_id = uuid4().hex
        read_request_id = uuid4().hex
        entity = IDNameEntity(
            id=uuid4().hex,
            name=self.faker.name(),
            created_at=datetime.now(),
            others={self.faker.word(): self.faker.sentence()},
        )
        response = await self.service.crupdate(create_request_id, entity)
        assert response.is_success

        ## Verify written record
        # Act
        response = await self.service.read_by_id(read_request_id, entity.id)

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None
        self.assertEqual(entity, response.payload)

        ## Delete record
        # Act
        response = await self.service.delete_by_id(delete_request_id, entity.id)

        # Assert
        self.assertTrue(response.is_success, response.message)

        ## Verify that record is deleted
        # Act
        response = await self.service.read_by_id(read_request_id, entity.id)

        # Assert
        self.assertFalse(response.is_success, response.message)
        self.assertEqual(response.code, 404)

    async def test_read_many(self) -> None:
        # Arrange
        entities = sorted(
            [
                IDNameEntity(
                    id=uuid4().hex,
                    name=self.faker.name(),
                    created_at=datetime.now(),
                )
                for _ in range(17)
            ],
            key=lambda entity: entity.name,
        )
        for entity in entities:
            crupdate_response = await self.service.crupdate(uuid4().hex, entity)
            assert crupdate_response.is_success

        read_request_id = uuid4().hex
        page_size = 5
        page_num = 1

        # Act
        response = await self.service.read_many(read_request_id, page_size, page_num)

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None
        self.assertEqual(response.payload, entities[:page_size])
