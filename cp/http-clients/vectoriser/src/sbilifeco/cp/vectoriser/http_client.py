from __future__ import annotations
from sbilifeco.cp.common.http.client import HttpClient, Request
from sbilifeco.boundaries.vectoriser import BaseVectoriser
from sbilifeco.cp.vectoriser.paths import VectoriserPaths
from sbilifeco.models.base import Response


class VectoriserHttpClient(HttpClient, BaseVectoriser):
    async def vectorise(
        self, request_id: str, material: str | bytes | bytearray
    ) -> Response[list[float | int]]:
        try:
            # Form
            url = f"{self.url_base}{VectoriserPaths.BY_REQUEST_ID.format(request_id=request_id)}"

            content_type = ""
            if isinstance(material, (bytes, bytearray)):
                content_type = "application/octet-stream"
            elif isinstance(material, str):
                content_type = "text/plain; charset=utf-8"

            req = Request(
                url=url,
                method="POST",
                data=str(material),
                headers={"Content-Type": content_type},
            )

            # Request
            response = await self.request_as_model(req)

            # Return
            return Response.ok(response)
        except Exception as e:
            return Response.error(e)
