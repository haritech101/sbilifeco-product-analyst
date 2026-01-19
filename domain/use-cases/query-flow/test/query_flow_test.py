from re import search
import sys

sys.path.append("./src")

from unittest import IsolatedAsyncioTestCase, result
from unittest.mock import AsyncMock, Base, patch

# Import the necessary service(s) here
from faker import Faker
from random import randint
from uuid import uuid4

from sbilifeco.models.base import Response
from sbilifeco.models.vectorisation import VectorisedRecord, RecordMetadata
from sbilifeco.flows.product_analyst.query_flow import QueryFlow, RatedAnswer
from sbilifeco.boundaries.vectoriser import BaseVectoriser
from sbilifeco.boundaries.vector_repo import BaseVectorRepo
from sbilifeco.boundaries.llm import ILLM


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        # Fakers and mocks
        self.fake = Faker()
        self.vectoriser: BaseVectoriser = AsyncMock(spec=BaseVectoriser)
        self.vector_repo: BaseVectorRepo = AsyncMock(spec=BaseVectorRepo)
        self.llm: ILLM = AsyncMock(spec=ILLM)

        # Initialise the service(s) here
        self.service = (
            QueryFlow()
            .set_vectoriser(self.vectoriser)
            .set_vector_repo(self.vector_repo)
            .set_llm(self.llm)
        )
        await self.service.async_init()

        ...

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        await self.service.async_shutdown()
        patch.stopall()
        ...

    async def test_request_search(self) -> None:
        # Act
        response = await self.service.request_search()

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None

        self.assertTrue(response.payload)
        ...

    async def test_search(self) -> None:
        # Arrange
        search_request_response = await self.service.request_search()
        assert search_request_response.payload is not None
        search_request_id = search_request_response.payload

        num_results = 3
        query = self.fake.sentence()
        vector = [randint(1, 100) for _ in range(256)]
        search_results = [
            VectorisedRecord(
                id=uuid4().hex,
                vector=[randint(1, 100) for _ in range(256)],
                document=self.fake.text(),
                metadata=RecordMetadata(
                    source_id=uuid4().hex,
                    source=" ".join(self.fake.words(3)),
                    chunk_num=i,
                ),
                score=randint(80, 100),
            )
            for i in range(num_results)
        ]
        llm_reply = self.fake.text()

        vectorise = patch.object(
            self.vectoriser,
            "vectorise",
            AsyncMock(return_value=Response.ok(vector)),
        ).start()

        search_by_vector = patch.object(
            self.vector_repo,
            "search_by_vector",
            AsyncMock(return_value=Response.ok(search_results)),
        ).start()

        generate_reply = patch.object(
            self.llm,
            "generate_reply",
            AsyncMock(return_value=Response.ok(llm_reply)),
        ).start()

        # Act
        query_flow_response = await self.service.search(
            search_request_id, query, num_results
        )

        # Assert
        self.assertTrue(query_flow_response.is_success, query_flow_response.message)
        assert query_flow_response.payload is not None
        rated_answer = query_flow_response.payload

        vectorise.assert_called_once_with(search_request_id, query)

        search_by_vector.assert_called_once_with(vector, num_results)

        generate_reply.assert_called_once()
        for search_result in search_results:
            self.assertIn(
                search_result.document, generate_reply.call_args_list[0][0][0]
            )
        self.assertIn(query, generate_reply.call_args_list[0][0][0])

        self.assertIn(rated_answer.answer, llm_reply)
