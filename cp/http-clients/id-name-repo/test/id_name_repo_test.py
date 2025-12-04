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
from datetime import datetime
from sbilifeco.models.base import Response

# Import the necessary service(s) here
from sbilifeco.boundaries.id_name_repo import IDNameEntity, BaseIDNameRepo
from sbilifeco.cp.id_name_repo.http_server import IDNameRepoHttpServer
from sbilifeco.cp.id_name_repo.http_client import IDNameRepoHttpClient


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))

        # Initialise the service(s) here
        self.faker = Faker()

        self.repo = AsyncMock(spec=BaseIDNameRepo)

        self.http_service = IDNameRepoHttpServer()
        (self.http_service.set_id_name_repo(self.repo).set_http_port(http_port))
        await self.http_service.listen()

        # Initialise the client(s) here
        self.http_client = IDNameRepoHttpClient()
        (self.http_client.set_proto("http").set_host("localhost").set_port(http_port))

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        await self.http_service.stop()
        patch.stopall()

    async def test_crupdate(self) -> None:
        # Arrange
        fn_crupdate = patch.object(
            self.repo, "crupdate", AsyncMock(return_value=Response.ok(None))
        ).start()
        crupdate_request_id = uuid4().hex
        entity = IDNameEntity(
            id=uuid4().hex, name=self.faker.name(), created_at=datetime.now()
        )

        # Act
        response = await self.http_client.crupdate(crupdate_request_id, entity)

        # Assert
        self.assertTrue(response.is_success, response.message)
        fn_crupdate.assert_called_once_with(crupdate_request_id, entity)

    async def test_delete(self) -> None:
        # Arrange
        fn_delete = patch.object(
            self.repo, "delete_by_id", AsyncMock(return_value=Response.ok(None))
        ).start()
        request_id = uuid4().hex
        entity_id = uuid4().hex

        # Act
        response = await self.http_client.delete_by_id(request_id, entity_id)

        # Assert
        self.assertTrue(response.is_success, response.message)
        fn_delete.assert_called_once_with(request_id, entity_id)

    async def test_read_by_id(self) -> None:
        # Arrange
        fn_delete = patch.object(
            self.repo, "read_by_id", AsyncMock(return_value=Response.ok(None))
        ).start()
        request_id = uuid4().hex
        entity_id = uuid4().hex

        # Act
        response = await self.http_client.read_by_id(request_id, entity_id)

        # Assert
        self.assertTrue(response.is_success, response.message)
        fn_delete.assert_called_once_with(request_id, entity_id)

    async def test_read_many(self) -> None:
        # Arrange
        fn_read_many = patch.object(
            self.repo, "read_many", AsyncMock(return_value=Response.ok([]))
        ).start()

        request_id = uuid4().hex
        page_size = 50
        page_num = 3

        # Act
        response = await self.http_client.read_many(request_id, page_size, page_num)

        # Assert
        self.assertTrue(response.is_success, response.message)
        fn_read_many.assert_called_once_with(request_id, page_size, page_num)
