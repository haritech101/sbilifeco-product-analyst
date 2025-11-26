import sys

sys.path.append("./src")

from unittest import IsolatedAsyncioTestCase

from dotenv import load_dotenv

# Import the necessary service(s) here
from sbilifeco.gateways.readers.pdf.docling_reader import DoclingReader


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        # Initialise the service(s) here
        self.service = DoclingReader()
        await self.service.async_init()

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        await self.service.async_shutdown()
        ...

    async def test_read_chunk(self) -> None:
        # Arrange
        read_response = await self.service.read_material(
            "file://.local/saral-jeevan-beema.pdf"
        )
        assert read_response.payload is not None
        material_id = read_response.payload

        # Act
        chunk_response = await self.service.read_next_chunk(material_id)

        # Assert
        self.assertTrue(chunk_response.is_success, chunk_response.message)
        assert chunk_response.payload is not None, chunk_response.message

        # Print all chunks
        while chunk_response.is_success and chunk_response.payload is not None:
            chunk_response = await self.service.read_next_chunk(material_id)

        self.assertTrue(chunk_response.is_success, chunk_response.message)

    async def test_read_chunk_from_bytes(self) -> None:
        # Arrange
        pdf_as_bytes = b""
        with open(".local/saral-jeevan-beema.pdf", "rb") as pdf_file:
            pdf_as_bytes = pdf_file.read()

        read_response = await self.service.read_material(pdf_as_bytes)
        assert read_response.payload is not None
        material_id = read_response.payload

        # Act
        chunk_response = await self.service.read_next_chunk(material_id)

        # Assert
        self.assertTrue(chunk_response.is_success, chunk_response.message)
        assert chunk_response.payload is not None, chunk_response.message

        # Print all chunks
        while chunk_response.is_success and chunk_response.payload is not None:
            chunk_response = await self.service.read_next_chunk(material_id)

        self.assertTrue(chunk_response.is_success, chunk_response.message)
