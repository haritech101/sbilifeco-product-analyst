from __future__ import annotations
from fastapi import Request
from sbilifeco.models.base import Response
from sbilifeco.cp.common.http.server import HttpServer
from sbilifeco.boundaries.material_reader import BaseMaterialReader
from sbilifeco.cp.material_reader.paths import MaterialReaderPaths


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
