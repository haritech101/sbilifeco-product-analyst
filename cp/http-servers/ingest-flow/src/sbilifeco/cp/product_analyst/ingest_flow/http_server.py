from __future__ import annotations
from typing import Annotated
from fastapi import Path, UploadFile
from sbilifeco.cp.common.http.server import HttpServer
from sbilifeco.boundaries.product_analyst.ingest_flow import BaseIngestFlow
from sbilifeco.cp.product_analyst.ingest_flow.paths import IngestFlowPaths
from sbilifeco.models.base import Response


class IngestFlowHttpServer(HttpServer):
    def __init__(self) -> None:
        super().__init__()
        self.flow: BaseIngestFlow

    def set_ingest_flow(self, ingest_flow: BaseIngestFlow) -> IngestFlowHttpServer:
        self.flow = ingest_flow
        return self

    def build_routes(self) -> None:
        super().build_routes()

        @self.post(IngestFlowPaths.BASE)
        async def request_ingestion() -> Response[str]:
            try:
                # Validate request
                ...

                # Triage request
                ...

                # Gateway call
                response = await self.flow.request_ingestion()
                if not response.is_success:
                    return Response.fail(response.message, response.code)
                elif response.payload is None:
                    return Response.fail(
                        "Ingestion request ID is inexplicably empty", 500
                    )
                ingestion_request_id = response.payload

                # Return response
                return Response.ok(ingestion_request_id)
            except Exception as e:
                return Response.error(e)

        @self.post(IngestFlowPaths.BY_ID)
        async def ingest(
            ingest_request_id: Annotated[str, Path()],
            title: UploadFile,
            material: UploadFile,
        ) -> Response[None]:
            try:
                # Validate request
                ...

                # Triage request
                title_as_bytes = await title.read()
                title_as_str = title_as_bytes.decode()

                material_untyped: str | bytes = ""
                material_as_bytes = await material.read()
                if (material.content_type or "").startswith("text/"):
                    material_untyped = material_as_bytes.decode()
                else:
                    material_untyped = material_as_bytes

                # Gateway call
                response = await self.flow.ingest(
                    ingest_request_id, title_as_str, material_untyped
                )

                # Return response
                return Response.ok(None)
            except Exception as e:
                return Response.error(e)
