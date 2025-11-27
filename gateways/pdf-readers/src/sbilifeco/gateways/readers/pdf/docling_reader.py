from __future__ import annotations

from io import BufferedIOBase, RawIOBase, TextIOBase, BytesIO
from json import load
from pathlib import Path
from typing import AsyncGenerator, cast
from uuid import uuid4

from docling.document_converter import DocumentConverter
from docling.datamodel.document import ConversionResult
from docling_core.types.doc.document import DoclingDocument, GroupItem, TableItem
from docling_core.types.doc.labels import DocItemLabel, GroupLabel
from docling_core.types.io import DocumentStream
from sbilifeco.boundaries.material_reader import BaseMaterialReader
from sbilifeco.models.base import Response
from sbilifeco.cp.common.http.client import HttpClient, Request


class DoclingPaths:
    BASE = "/v1"
    CHUNK_FILE = BASE + "/chunk/hybrid/file"


class DoclingReader(BaseMaterialReader, HttpClient):
    def __init__(self):
        BaseMaterialReader.__init__(self)
        HttpClient.__init__(self)
        self.set_proto("http")
        self.set_host("localhost")
        self.set_port(80)
        self.chunks: dict[str, AsyncGenerator[str | bytes | bytearray]] = {}

    def set_doclingserve_proto(self, proto: str) -> DoclingReader:
        self.set_proto(proto)
        return self

    def set_doclingserve_host(self, host: str) -> DoclingReader:
        self.set_host(host)
        return self

    def set_doclingserve_port(self, port: int) -> DoclingReader:
        self.set_port(port)
        return self

    async def async_init(self) -> None: ...

    async def async_shutdown(self) -> None: ...

    async def read_material(
        self,
        material: str | bytes | bytearray | RawIOBase | BufferedIOBase | TextIOBase,
    ) -> Response[str]:
        try:
            material_id = str(uuid4())
            # converter = DocumentConverter()

            if isinstance(
                material, (str, bytes, bytearray, RawIOBase, BufferedIOBase, TextIOBase)
            ):
                # result: ConversionResult | None = None
                material_as_bytes = b""

                if isinstance(material, str):
                    if material.startswith("file://"):
                        the_path = Path(material[7:])
                        if not the_path.exists():
                            return Response.fail("Invalid material")

                        with open(the_path, "rb") as open_material:
                            material_as_bytes = open_material.read()
                    else:
                        material_as_bytes = material.encode()
                elif isinstance(material, (bytes, bytearray)):
                    material_as_bytes = bytes(material)
                elif isinstance(material, TextIOBase):
                    material_as_bytes = material.read().encode()
                elif isinstance(material, (RawIOBase, BufferedIOBase)):
                    material_as_bytes = material.read()

                req = Request(
                    url=f"{self.url_base}{DoclingPaths.CHUNK_FILE}",
                    method="POST",
                    files={
                        "files": (
                            f"{material_id}",
                            material_as_bytes,
                            "application/octet-stream",
                        )
                    },
                )

                docling_response = await self.request_as_binary(req)
                if not docling_response.is_success:
                    return Response.fail(
                        docling_response.message, docling_response.code
                    )
                elif not docling_response.payload:
                    return Response.fail("Docling payload is inexplicably empty", 500)

                docling_payload_as_bytes = docling_response.payload
                docling_payload = load(BytesIO(docling_payload_as_bytes))

                self.chunks[material_id] = self._get_next_chunk(
                    docling_payload.get("chunks", [])
                )
                return Response.ok(material_id)

            return Response.fail("Unsupported material type", 400)
        except Exception as e:
            return Response.error(e)

    async def read_next_chunk(
        self, material_id: str
    ) -> Response[str | bytes | bytearray]:
        try:
            if material_id not in self.chunks:
                return Response.fail(
                    f"No material with ID {material_id} found. Did you check the result of read_material() for errors?",
                    404,
                )

            chunks = self.chunks.get(material_id)
            if not chunks:
                return Response.fail(f"Material {material_id} is inexplicably blank")

            try:
                return Response.ok(await anext(self.chunks[material_id]))
            except StopAsyncIteration:
                return Response.ok(None)
        except Exception as e:
            return Response.error(e)

    async def _get_next_chunk(
        self, chunks: list[dict]
    ) -> AsyncGenerator[str | bytes | bytearray]:
        for chunk in chunks:
            yield chunk.get("text", "")
