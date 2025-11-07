from __future__ import annotations
from typing import Annotated
from fastapi import Body, Path
from sbilifeco.cp.common.http.server import HttpServer
from sbilifeco.boundaries.vector_repo import BaseVectorRepo
from sbilifeco.cp.vector_repo.paths import VectorRepoPaths
from sbilifeco.models.base import Response
from sbilifeco.models.vectorisation import VectorisedRecord


class VectorRepoHttpServer(HttpServer):
    def __init__(self) -> None:
        super().__init__()
        self.vector_repo: BaseVectorRepo

    def set_vector_repo(self, vector_repo: BaseVectorRepo) -> VectorRepoHttpServer:
        self.vector_repo = vector_repo
        return self

    def build_routes(self) -> None:
        super().build_routes()

        @self.post(VectorRepoPaths.BASE)
        async def crupdate(
            record: Annotated[VectorisedRecord, Body()],
        ) -> Response[None]:
            try:
                # Validate
                ...

                # Triage request
                ...

                # Gateway call
                response = await self.vector_repo.crupdate(record)

                # Triage return
                ...

                # Return
                return response
            except Exception as e:
                return Response.error(e)

        @self.delete(VectorRepoPaths.BY_ID)
        async def delete_by_id(id: Annotated[str, Path()]) -> Response[None]:
            try:
                # Validate
                ...

                # Triage
                ...

                # Gateway call
                response = await self.vector_repo.delete_by_id(id)

                # Triage
                ...

                # Return
                return response
            except Exception as e:
                return Response.error(e)

        @self.post(VectorRepoPaths.DELETE_BY_CRITERIA)
        async def delete_by_criteria(
            criteria: Annotated[dict, Body()],
        ) -> Response[None]:
            try:
                # Validate
                ...

                # Triage
                ...

                # Gateway call
                response = await self.vector_repo.delete_by_criteria(criteria)

                # Triage
                ...

                # Return
                return response
            except Exception as e:
                return Response.error(e)

        @self.get(VectorRepoPaths.BY_ID)
        async def read_by_id(id: Annotated[str, Path()]) -> Response[VectorisedRecord]:
            try:
                # Validate
                ...

                # Triage
                ...

                # Gateway call
                response = await self.vector_repo.read_by_id(id)

                # Triage
                ...

                # Return
                return response
            except Exception as e:
                return Response.error(e)

        @self.post(VectorRepoPaths.SEARCH_BY_CRITERIA)
        async def read_by_criteria(
            criteria: Annotated[dict, Body()],
        ) -> Response[list[VectorisedRecord]]:
            try:
                # Validate
                ...

                # Triage
                ...

                # Gateway call
                response = await self.vector_repo.read_by_criteria(criteria)

                # Triage
                ...

                # Return
                return response
            except Exception as e:
                return Response.error(e)

        @self.post(VectorRepoPaths.BY_VECTOR)
        async def search_by_vector(
            vector: Annotated[list[float], Body()],
        ) -> Response[list[VectorisedRecord]]:
            try:
                # Validate
                ...

                # Triage
                ...

                # Gateway call
                response = await self.vector_repo.search_by_vector(vector)

                # Triage
                ...

                # Return
                return response
            except Exception as e:
                return Response.error(e)
