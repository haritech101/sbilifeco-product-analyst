from __future__ import annotations
from typing import Sequence
from sbilifeco.models.base import Response
from sbilifeco.boundaries.id_name_repo import IDNameEntity, BaseIDNameRepo
from sbilifeco.cp.common.http.server import HttpServer
from sbilifeco.cp.id_name_repo.paths import IDNameOp, Paths, Pagination


class IDNameRepoHttpServer(HttpServer):
    def __init__(self) -> None:
        super().__init__()
        self.repo: BaseIDNameRepo

    def set_id_name_repo(self, repo: BaseIDNameRepo) -> IDNameRepoHttpServer:
        self.repo = repo
        return self

    def build_routes(self) -> None:
        super().build_routes()

        @self.post(Paths.UPSERT_REQUESTS)
        async def crupdate(op: IDNameOp) -> Response[None]:
            try:
                # Validate request
                if not isinstance(op.params, IDNameEntity):
                    return Response.fail("Entity is not in the required format", 400)

                # Triage request
                request_id = op.request_id
                entity = op.params

                # Call gateway
                res = await self.repo.crupdate(request_id, entity)

                # Return response
                return res
            except Exception as e:
                return Response.error(e)

        @self.post(Paths.DELETE_REQUESTS)
        async def delete_by_id(op: IDNameOp) -> Response[None]:
            try:
                # Validate request
                if not isinstance(op.params, str):
                    return Response.fail(
                        "Deletion expects the string ID of the entity to be deleted",
                        400,
                    )

                # Triage request
                request_id = op.request_id
                entity_id = op.params

                # Gateway call
                res = await self.repo.delete_by_id(request_id, entity_id)

                # Triage response
                ...

                # Return response
                return res
            except Exception as e:
                return Response.error(e)

        @self.post(Paths.READ_BY_ID_REQUESTS)
        async def read_by_id(op: IDNameOp) -> Response[IDNameEntity]:
            try:
                # Validate request
                if not isinstance(op.params, str):
                    return Response.fail(
                        "Reading by ID expects a string ID as a parameter", 400
                    )

                # Triage request
                request_id = op.request_id
                entity_id = op.params

                # Gateway call
                res = await self.repo.read_by_id(request_id, entity_id)

                # Triage response
                ...

                # Return response
                return res
            except Exception as e:
                return Response.error(e)

        @self.post(Paths.READ_MANY_REQUESTS)
        async def read_many(op: IDNameOp) -> Response[Sequence[IDNameEntity]]:
            try:
                # Validate request
                if not isinstance(op.params, Pagination):
                    return Response.fail(
                        "Reading list of entities can take only optional pagination parameters page_size and page_num",
                        400,
                    )

                # Triage request
                request_id = op.request_id
                pagination = op.params

                # Gateway call
                res = await self.repo.read_many(
                    request_id, pagination.page_size, pagination.page_num
                )

                # Triage response
                ...

                # Return response
                return res
            except Exception as e:
                return Response.error(e)
