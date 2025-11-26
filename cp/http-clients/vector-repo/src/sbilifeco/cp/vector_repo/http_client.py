from __future__ import annotations

from typing import Any

from sbilifeco.boundaries.vector_repo import BaseVectorRepo
from sbilifeco.cp.common.http.client import HttpClient, Request
from sbilifeco.cp.vector_repo.paths import VectorRepoPaths
from sbilifeco.models.base import Response
from sbilifeco.models.vectorisation import VectorisedRecord


class VectorRepoHttpClient(HttpClient, BaseVectorRepo):
    async def crupdate(self, record: VectorisedRecord) -> Response[None]:
        try:
            # Form
            url = f"{self.url_base}{VectorRepoPaths.BASE}"

            req = Request(
                url=url,
                method="POST",
                json=record.model_dump(),
            )

            # Request
            response = await self.request_as_model(req)

            # Return
            return response
        except Exception as e:
            return Response.error(e)

    async def delete_by_id(self, record_id: str) -> Response[None]:
        try:
            # Form
            url = f"{self.url_base}{VectorRepoPaths.BY_ID.format(id=record_id)}"

            req = Request(url=url, method="DELETE")

            # Request
            response = await self.request_as_model(req)

            # Triage
            ...

            # Return
            return response
        except Exception as e:
            return Response.error(e)

    async def delete_by_criteria(self, criteria: dict[str, Any]) -> Response[None]:
        try:
            # Form
            url = f"{self.url_base}{VectorRepoPaths.DELETE_BY_CRITERIA}"

            req = Request(url=url, method="POST", json=criteria)

            # Request
            response = await self.request_as_model(req)

            # Triage
            ...

            # Return
            return response
        except Exception as e:
            return Response.error(e)

    async def read_by_id(self, record_id: str) -> Response[VectorisedRecord]:
        try:
            # Form
            url = f"{self.url_base}{VectorRepoPaths.BY_ID.format(id=record_id)}"

            req = Request(url=url, method="GET")

            # Request
            response = await self.request_as_model(req)

            # Triage
            ...

            # Return
            return response
        except Exception as e:
            return Response.error(e)

    async def read_by_criteria(
        self, criteria: dict[str, Any]
    ) -> Response[list[VectorisedRecord]]:
        try:
            # Form
            url = f"{self.url_base}{VectorRepoPaths.SEARCH_BY_CRITERIA}"

            req = Request(url=url, method="POST", json=criteria)

            # Request
            response = await self.request_as_model(req)

            # Triage
            if response.payload:
                response.payload = [
                    VectorisedRecord.model_validate(map) for map in response.payload
                ]

            # Return
            return response
        except Exception as e:
            return Response.error(e)

    async def search_by_vector(
        self, vector: list[float], num_results: int = 5
    ) -> Response[list[VectorisedRecord]]:
        try:
            # Form
            url = f"{self.url_base}{VectorRepoPaths.BY_VECTOR}"

            req = Request(url=url, method="POST", json=vector)

            # Request
            response = await self.request_as_model(req)

            # Triage
            if response.payload:
                response.payload = [
                    VectorisedRecord.model_validate(map) for map in response.payload
                ]

            # Return
            return response
        except Exception as e:
            return Response.error(e)
