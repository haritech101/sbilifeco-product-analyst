import sys

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase
from dotenv import load_dotenv
from envvars import EnvVars, Defaults
from uuid import uuid4

# Import the necessary service(s) here
from sbilifeco.gateways.file_system_chromadb import FileSystemChromDB


class FileSystemChromaDBTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()
        db_path = getenv(EnvVars.db_path, Defaults.db_path)

        # Initialise the service(s) here
        self.service = FileSystemChromDB()
        self.service.set_db_path(db_path)
        await self.service.async_init()
        ...

        # Initialise the client(s) here
        ...

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        await self.service.async_shutdown()
        ...

    async def test(self) -> None:
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
