from __future__ import annotations
from fastapi import Request
from sbilifeco.models.base import Response
from sbilifeco.cp.common.http.server import HttpServer
from sbilifeco.boundaries.vectoriser import BaseVectoriser
from sbilifeco.cp.vectoriser.paths import VectoriserPaths


class VectoriserHttpServer(HttpServer):
    def __init__(self):
        super().__init__()
        self.vectoriser: BaseVectoriser

    def set_vectoriser(self, vectoriser: BaseVectoriser) -> VectoriserHttpServer:
        self.vectoriser = vectoriser
        return self

    async def listen(self) -> None:
        await super().listen()

    async def stop(self) -> None:
        return await super().stop()

    def build_routes(self) -> None:
        super().build_routes()

        @self.post(VectoriserPaths.BY_REQUEST_ID)
        async def vectorise(req: Request) -> Response[list[int | float]]:
            try:
                # Triage
                request_id = req.path_params.get("request_id")
                if not request_id:
                    return Response.fail("Missing request ID in URL", 400)

                content_type = req.headers.get("Content-Type", "")
                attached_data: str | bytes | bytearray = ""
                if content_type == "application/octet-stream":
                    attached_data = await req.body()
                elif content_type.startswith("text/plain"):
                    attached_data = (await req.body()).decode("utf-8")

                # Use gateway
                response = await self.vectoriser.vectorise(request_id, attached_data)

                # Return
                return response
            except Exception as e:
                return Response.error(e)
