from __future__ import annotations
from typing import Sequence
from sbilifeco.models.base import Response
from sbilifeco.boundaries.id_name_repo import BaseIDNameRepo, IDNameEntity
from sbilifeco.cp.common.http.client import HttpClient, Request
from sbilifeco.cp.id_name_repo.paths import Paths, IDNameOp, Pagination


class IDNameRepoHttpClient(BaseIDNameRepo, HttpClient):
    def __init__(self) -> None:
        BaseIDNameRepo.__init__(self)
        HttpClient.__init__(self)
        self.proto = "http"
        self.host = "localhost"
        self.port = 80

    async def crupdate(self, request_id: str, entity: IDNameEntity) -> Response[None]:
        try:
            # Form request
            url = f"{self.url_base}{Paths.UPSERT_REQUESTS}"
            payload = IDNameOp(request_id=request_id, params=entity).model_dump()
            req = Request(
                url=url,
                method="POST",
                json=payload,
            )

            # Send request
            res = await self.request_as_model(req)

            # Triage response
            ...

            # Return response
            return Response.ok(res)
        except Exception as e:
            return Response.error(e)

    async def delete_by_id(self, request_id: str, entity_id: str) -> Response[None]:
        try:
            # Form request
            url = f"{self.url_base}{Paths.DELETE_REQUESTS}"
            payload = IDNameOp(request_id=request_id, params=entity_id).model_dump()
            req = Request(url=url, method="POST", json=payload)

            # Send request
            res = await self.request_as_model(req)

            # Triage response
            ...

            # Return response
            return res
        except Exception as e:
            return Response.error(e)

    async def read_by_id(
        self, request_id: str, entity_id: str
    ) -> Response[IDNameEntity]:
        try:
            # Form request
            url = f"{self.url_base}{Paths.READ_BY_ID_REQUESTS}"
            payload = IDNameOp(request_id=request_id, params=entity_id).model_dump()
            req = Request(url=url, method="POST", json=payload)

            # Send request
            res = await self.request_as_model(req)

            # Triage response
            if res.payload:
                res.payload = IDNameEntity.model_validate(res.payload)

            # Return response
            return res
        except Exception as e:
            return Response.error(e)

    async def read_many(
        self, request_id: str, page_size: int = -1, page_num: int = -1
    ) -> Response[Sequence[IDNameEntity]]:
        try:
            # Form request
            url = f"{self.url_base}{Paths.READ_MANY_REQUESTS}"
            payload = IDNameOp(
                request_id=request_id,
                params=Pagination(page_size=page_size, page_num=page_num),
            ).model_dump()
            req = Request(url=url, method="POST", json=payload)

            # Send request
            res = await self.request_as_model(req)

            # Triage response
            if res.payload:
                res.payload = [IDNameEntity.model_validate(map) for map in res.payload]

            # Return response
            return res
        except Exception as e:
            return Response.error(e)
