from __future__ import annotations
from uuid import uuid4
from typing import Any
from sbilifeco.boundaries.product_analyst.query_flow import (
    BaseQueryFlow,
    RatedAnswer,
    RatedSource,
)
from sbilifeco.models.base import Response
from sbilifeco.boundaries.vectoriser import BaseVectoriser
from sbilifeco.boundaries.vector_repo import BaseVectorRepo
from sbilifeco.boundaries.llm import ILLM


class QueryFlow(BaseQueryFlow):
    def __init__(self) -> None:
        super().__init__()
        self.search_requests: dict[str, Any] = {}
        self.vectoriser: BaseVectoriser
        self.vector_repo: BaseVectorRepo
        self.llm: ILLM

    def set_vectoriser(self, vectoriser: BaseVectoriser) -> QueryFlow:
        self.vectoriser = vectoriser
        return self

    def set_vector_repo(self, vector_repo: BaseVectorRepo) -> QueryFlow:
        self.vector_repo = vector_repo
        return self

    def set_llm(self, llm: ILLM) -> QueryFlow:
        self.llm = llm
        return self

    async def async_init(self) -> None: ...

    async def async_shutdown(self) -> None: ...

    async def request_search(self) -> Response[str]:
        try:
            request_id = uuid4().hex
            self.search_requests[request_id] = {}
            return Response.ok(request_id)
        except Exception as e:
            return Response.error(e)

    async def search(
        self, search_request_id: str, query: str, num_results: int = 5
    ) -> Response[RatedAnswer]:
        try:
            # Validate
            if search_request_id not in self.search_requests:
                return Response.fail(
                    f"Search request {search_request_id} not found", 404
                )

            # Vectorise the query
            vector_response = await self.vectoriser.vectorise(search_request_id, query)
            if not vector_response.is_success:
                return Response.fail(vector_response.message, vector_response.code)
            elif vector_response.payload is None:
                return Response.fail("Search term vector is inexplicably empty", 500)
            search_vector = vector_response.payload

            # Semantic search
            search_response = await self.vector_repo.search_by_vector(
                search_vector, num_results
            )
            if not search_response.is_success:
                return Response.fail(search_response.message, search_response.code)
            elif search_response.payload is None:
                return Response.fail("Search results are inexplicably empty", 500)
            search_results = search_response.payload

            # Generate LLM answer
            context = (
                f"You are a product analyst who reads product descriptions and answers questions.\n\n"
                f"Product description follows:\n"
                f"{"\n\n".join([str(result.document) for result in search_results])}"
                f"\n\nNow please answer the following question:\n\n"
                f"{query}\n\n"
            )
            llm_response = await self.llm.generate_reply(context)
            if not llm_response.is_success:
                return Response.fail(llm_response.message, llm_response.code)
            elif llm_response.payload is None:
                return Response.fail("LLM reply is inexplicably empty", 500)
            llm_reply = llm_response.payload

            # Triage
            rated_answer = RatedAnswer(
                answer=llm_reply,
                sources=[
                    RatedSource(
                        source=search_result.metadata.source, rating=search_result.score
                    )
                    for search_result in search_results
                ],
            )

            # The search request is done
            if search_request_id in self.search_requests:
                del self.search_requests[search_request_id]

            # Return
            return Response.ok(rated_answer)
        except Exception as e:
            return Response.error(e)
