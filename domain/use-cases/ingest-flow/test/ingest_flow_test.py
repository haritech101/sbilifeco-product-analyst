import sys

sys.path.append("./src")

from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from random import randint

from dotenv import load_dotenv
from faker import Faker
from sbilifeco.boundaries.material_reader import BaseMaterialReader
from sbilifeco.boundaries.vector_repo import BaseVectorRepo
from sbilifeco.boundaries.vectoriser import BaseVectoriser
from sbilifeco.boundaries.id_name_repo import BaseIDNameRepo, IDNameEntity
from sbilifeco.models.base import Response

# Import the necessary service(s) here
from sbilifeco.flows.product_analyst.ingest_flow import IngestFlow


class IngestFlowTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        # Faking and Patching
        self.faker = Faker()

        self.material_reader: BaseMaterialReader = AsyncMock(spec=BaseMaterialReader)
        self.vectoriser: BaseVectoriser = AsyncMock(spec=BaseVectoriser)
        self.vector_repo: BaseVectorRepo = AsyncMock(spec=BaseVectorRepo)
        self.id_name_repo: BaseIDNameRepo = AsyncMock(spec=BaseIDNameRepo)

        # Initialise the service(s) here
        self.service = (
            IngestFlow()
            .set_material_reader(self.material_reader)
            .set_vectoriser(self.vectoriser)
            .set_vector_repo(self.vector_repo)
            .set_id_name_repo(self.id_name_repo)
        )
        await self.service.async_init()

        ...

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        await self.service.async_shutdown()
        patch.stopall()
        ...

    async def test_request_ingestion(self) -> None:
        # Act
        reqing_response = await self.service.request_ingestion()

        # Assert
        self.assertTrue(reqing_response.is_success, reqing_response.message)
        assert reqing_response.payload is not None
        ...

    async def test_ingest(self) -> None:
        # Arrange
        title = self.faker.sentence()
        read_material_id = uuid4()

        num_chunks = 3
        chunks: list[str | None] = [self.faker.paragraph() for _ in range(num_chunks)]
        chunks.append(None)  # Indicate end of chunks

        read_material = patch.object(
            self.material_reader,
            "read_material",
            return_value=Response.ok(read_material_id),
        ).start()
        get_next_chunk = patch.object(
            self.material_reader,
            "read_next_chunk",
            side_effect=[Response.ok(chunk) for chunk in chunks],
        ).start()
        vectorise = patch.object(
            self.vectoriser,
            "vectorise",
            return_value=Response.ok([randint(0, 100) for _ in range(256)]),
        ).start()
        crupdate_material = patch.object(
            self.vector_repo,
            "crupdate",
            return_value=Response.ok(None),
        ).start()
        crupdate_entity = patch.object(
            self.id_name_repo, "crupdate", return_value=Response.ok(None)
        ).start()

        request_ingestion_response = await self.service.request_ingestion()
        assert request_ingestion_response.payload is not None
        ingestion_request_id = request_ingestion_response.payload

        sample_data = "\n\n".join(self.faker.paragraphs(5))

        # Act
        ingest_response = await self.service.ingest(
            ingestion_request_id,
            title,
            sample_data,
        )

        # Assert
        self.assertTrue(ingest_response.is_success, ingest_response.message)

        # Reading of material should be requested
        read_material.assert_called_once_with(sample_data)

        # Material ID and title should be stored as an entity
        crupdate_entity.assert_called_once()
        entity = crupdate_entity.call_args_list[0][0][1]
        assert isinstance(entity, IDNameEntity)

        self.assertEqual(entity.name, title)

        # Chunks should be read until none are left
        get_next_chunk.assert_called()
        self.assertEqual(get_next_chunk.call_count, num_chunks + 1)
        get_next_chunk.assert_any_call(read_material_id)

        # Chunks should be vectorised
        vectorise.assert_called()
        self.assertEqual(vectorise.call_count, num_chunks)

        crupdate_material.assert_called()
        self.assertEqual(crupdate_material.call_count, num_chunks)

        for i in range(num_chunks):
            self.assertEqual(vectorise.call_args_list[i][0][1], chunks[i])
            self.assertEqual(
                crupdate_material.call_args_list[i][0][0].document, chunks[i]
            )
            self.assertEqual(
                crupdate_material.call_args_list[i][0][0].metadata.source, title
            )
        ...
