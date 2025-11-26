from __future__ import annotations

from io import BufferedIOBase, RawIOBase, TextIOBase
from pathlib import Path
from typing import AsyncGenerator, cast
from uuid import uuid4

from docling.document_converter import DocumentConverter
from docling_core.types.doc.document import DoclingDocument, GroupItem, TableItem
from docling_core.types.doc.labels import DocItemLabel, GroupLabel
from sbilifeco.boundaries.material_reader import BaseMaterialReader
from sbilifeco.models.base import Response


class DoclingReader(BaseMaterialReader):
    def __init__(self):
        super().__init__()
        self.chunks: dict[str, AsyncGenerator[str | bytes | bytearray]] = {}

    async def async_init(self) -> None: ...

    async def async_shutdown(self) -> None: ...

    async def read_material(
        self,
        material: str | bytes | bytearray | RawIOBase | BufferedIOBase | TextIOBase,
    ) -> Response[str]:
        try:
            material_id = str(uuid4())
            converter = DocumentConverter()

            if isinstance(material, str):
                if material.startswith("file://"):
                    the_path = Path(material[7:])
                    if not the_path.exists():
                        return Response.fail("Invalid material")

                    result = converter.convert(the_path)
                    if result.errors:
                        return Response.fail(
                            f"Conversion failed: {";".join([e.error_message for e in result.errors])}"
                        )

                    print(
                        f"{material_id} parsed with confidence {result.confidence.layout_score}"
                    )

                    self.chunks[material_id] = self._get_next_chunk(result.document)

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
        self, doc: DoclingDocument
    ) -> AsyncGenerator[str | bytes | bytearray]:
        start = -1
        for i, segment in enumerate(doc.body.children):
            item = segment.resolve(doc)

            if (
                item.label in (DocItemLabel.TABLE, DocItemLabel.PICTURE)
                or item.label in GroupLabel
            ):
                if start != -1:
                    yield "\n".join(
                        [
                            segment.resolve(doc).text
                            for segment in doc.body.children[start:i]
                        ]
                    )
                    start = -1

            if item.label == DocItemLabel.PICTURE:
                continue
            elif item.label == DocItemLabel.TABLE:
                yield cast(TableItem, item).export_to_markdown()
            elif item.label in GroupLabel:
                children = cast(GroupItem, item).children
                yield "\n".join(
                    [
                        resolved.text if hasattr(resolved, "text") else ""
                        for resolved in [
                            group_item.resolve(doc).text for group_item in children
                        ]
                    ]
                )
            elif start == -1:
                start = i

        if start != -1:
            yield "\n".join(
                [
                    segment.resolve(doc).text
                    for segment in doc.body.children[start : len(doc.body.children)]
                ]
            )
