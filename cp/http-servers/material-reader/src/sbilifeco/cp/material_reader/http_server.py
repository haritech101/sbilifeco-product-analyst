from __future__ import annotations
from fastapi import Request
from sbilifeco.models.base import Response
from sbilifeco.cp.common.http.server import HttpServer
from sbilifeco.boundaries.material_reader import BaseMaterialReader
from sbilifeco.cp.material_reader.paths import MaterialReaderPaths
from fastapi.responses import StreamingResponse, PlainTextResponse


class MaterialReaderHttpServer(HttpServer):
    def __init__(self):
        HttpServer.__init__(self)
        self.material_reader: BaseMaterialReader

    def set_material_reader(
        self, reader: BaseMaterialReader
    ) -> MaterialReaderHttpServer:
        self.material_reader = reader
        return self

    def build_routes(self) -> None:
        super().build_routes()

        @self.post(MaterialReaderPaths.BASE)
        async def read_material(req: Request) -> Response[str]:
            try:
                # Triage
                content_type = req.headers.get("Content-Type", "text/plain")
                material: bytes | str = ""

                if content_type == "application/octet-stream":
                    material = await req.body()
                elif content_type.startswith("text/plain"):
                    material = (await req.body()).decode()

                # Gateway call
                response = await self.material_reader.read_material(material)

                # Return
                return response
            except Exception as e:
                return Response.error(e)

        @self.get(MaterialReaderPaths.NEXT_CHUNK)
        async def read_next_chunk(
            material_id: str,
        ) -> Response[str | bytes]:
            try:
                # Gateway call
                response = await self.material_reader.read_next_chunk(material_id)

                if isinstance(response.payload, bytearray):
                    response.payload = bytes(response.payload)

                # Return
                return response
            except Exception as e:
                return Response.error(e)

        @self.post(MaterialReaderPaths.STREAMS)
        async def read_and_chunk(req: Request):
            # Triage
            content_type = req.headers.get("Content-Type", "text/plain")
            material: bytes | str | None = None

            if content_type == "application/octet-stream":
                material = await req.body()
            elif content_type.startswith("text/plain"):
                material = (await req.body()).decode()

            if material is None:
                return PlainTextResponse(
                    "Unable to determine material type", status_code=400
                )

            # Gateway call
            response = await self.material_reader.read_and_chunk(material)

            # Triage response
            if not response.is_success:
                return PlainTextResponse(
                    f"Error reading material: {response.message}",
                    status_code=response.code,
                )

            if response.payload is None:
                return PlainTextResponse(
                    "Material to stream is inexplicable blank", status_code=500
                )

            async def __stream():
                if response.payload is None:
                    return

                async for chunk in response.payload:
                    yield chunk

            # Return
            return StreamingResponse(response.payload, media_type=content_type)
