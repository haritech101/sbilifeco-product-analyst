from __future__ import annotations
from io import BufferedIOBase, IOBase, RawIOBase, TextIOBase
from sbilifeco.boundaries.id_name_repo import IDNameEntity, SortDirection, SortField
from sbilifeco.boundaries.product_analyst.ingest_flow import BaseIngestFlow
from sbilifeco.cp.common.http.client import HttpClient, Request
from sbilifeco.models.base import Response
from sbilifeco.cp.product_analyst.ingest_flow.paths import (
    IngestFlowPaths,
    Pagination,
    SortDirection,
    SortField,
)


class IngestFlowHttpClient(HttpClient, BaseIngestFlow):
    def __init__(self) -> None:
        HttpClient.__init__(self)

    async def request_ingestion(self) -> Response[str]:
        try:
            # Form request
            url = f"{self.url_base}{IngestFlowPaths.BASE}"
            req = Request(method="POST", url=url)

            # Send request
            res = await self.request_as_model(req)

            # Triage response
            ...

            # Return response
            return res
        except Exception as e:
            return Response.error(e)

    async def ingest(
        self,
        ingestion_request: str,
        title: str,
        source: str | bytes | bytearray | TextIOBase | BufferedIOBase | RawIOBase,
    ) -> Response[None]:
        try:
            # Form request
            url = f"{self.url_base}{IngestFlowPaths.BY_ID.format(ingest_request_id=ingestion_request)}"

            content_type = ""
            triaged_source: str | bytes = ""

            if isinstance(source, (str, TextIOBase)):
                content_type = "text/plain; charset-utf-8"
            elif isinstance(source, (bytes, bytearray, BufferedIOBase, RawIOBase)):
                content_type = "application/octet-stream"

            if isinstance(source, (str, bytes)):
                triaged_source = source
            elif isinstance(source, bytearray):
                triaged_source = bytes(source)
            elif isinstance(source, IOBase):
                triaged_source = source.read()

            req = Request(
                url=url,
                method="POST",
                data={"title": title},
                files={
                    "material": ("material", triaged_source, content_type),
                },
            )

            # Send request
            response = await self.request_as_model(req)

            # Triage response
            ...

            # Return response
            return response
        except Exception as e:
            return Response.error(e)

    async def get_materials(
        self,
        page_size: int = -1,
        page: int = -1,
        sorts: dict[SortField, SortDirection] = {},
    ) -> Response[list[IDNameEntity]]:
        try:
            # Form request
            url = f"{self.url_base}{IngestFlowPaths.MATERIALS}"
            req = Request(
                url=url,
                method="POST",
                json=Pagination(
                    page_size=page_size, page_num=page, sorts=sorts
                ).model_dump(),
            )

            # Send request
            res = await self.request_as_model(req)

            # Triage response
            if res.payload is not None:
                res.payload = [
                    IDNameEntity.model_validate(item) for item in res.payload
                ]

            # Return response
            return res
        except Exception as e:
            return Response.error(e)
