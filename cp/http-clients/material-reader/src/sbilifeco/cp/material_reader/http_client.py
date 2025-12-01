from __future__ import annotations

from io import BufferedIOBase, RawIOBase, TextIOBase

from sbilifeco.boundaries.material_reader import BaseMaterialReader
from sbilifeco.cp.common.http.client import HttpClient, Request
from sbilifeco.models.base import Response
from sbilifeco.cp.material_reader.paths import MaterialReaderPaths


class MaterialReaderHttpClient(HttpClient, BaseMaterialReader):
    async def read_material(
        self,
        material: str | bytes | bytearray | RawIOBase | BufferedIOBase | TextIOBase,
    ) -> Response[str]:
        try:
            # Form
            url = f"{self.url_base}{MaterialReaderPaths.BASE}"

            content_type = ""
            to_be_posted: str | bytes | bytearray = ""
            if isinstance(material, (bytes, bytearray)):
                to_be_posted = material
                content_type = "application/octet-stream"
            elif isinstance(material, str):
                to_be_posted = material
                content_type = "text/plain; charset=utf-8"
            elif isinstance(material, (RawIOBase, BufferedIOBase)):
                content_type = "application/octet-stream"
                to_be_posted = material.read()
            elif isinstance(material, TextIOBase):
                content_type = "text/plain; charset-utf-8"
                to_be_posted = material.read()

            req = Request(
                url=url,
                method="POST",
                headers={"Content-Type": content_type},
                data=to_be_posted,
            )

            # Request
            response = await self.request_as_model(req)

            # Return
            return response
        except Exception as e:
            return Response.error(e)

    async def read_next_chunk(
        self, material_id: str
    ) -> Response[str | bytes | bytearray]:
        try:
            # Form
            url = f"{self.url_base}{MaterialReaderPaths.NEXT_CHUNK.format(material_id=material_id)}"

            req = Request(
                url=url,
                method="GET",
            )

            # Request
            res = await self.request_as_model(req)

            # Return
            return res
        except Exception as e:
            return Response.error(e)
