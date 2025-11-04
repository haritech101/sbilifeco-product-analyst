from __future__ import annotations
from io import BufferedIOBase, RawIOBase, TextIOBase
from typing import Protocol
from sbilifeco.models.base import Response
from uuid import uuid4


class BaseMaterialReader:
    def __init__(self) -> None:
        self.listeners: list[IMaterialReaderListener] = []
        self.materials: dict[
            str, str | bytes | bytearray | RawIOBase | BufferedIOBase | TextIOBase
        ] = {}

    def add_listener(self, listener: IMaterialReaderListener) -> None:
        """Adds a listener to the Material Reader."""
        self.listeners.append(listener)

    async def read_material(
        self,
        material: str | bytes | bytearray | RawIOBase | BufferedIOBase | TextIOBase,
    ) -> Response[str]:
        """Reads material and returns a Response containing an ID that can be used to fetch the material later."""
        material_id = str(uuid4())
        self.materials[material_id] = material
        return Response.ok(material_id)

    async def read_next_chunk(
        self, material_id: str
    ) -> Response[str | bytes | bytearray]:
        """Reads the next chunk of material and returns a Response containing the chunk data."""
        ...


class IMaterialReaderListener(Protocol):
    async def on_material_read(
        self,
        response: Response[str],
    ) -> None:
        """Called when material has been read."""
        """
        Args:
            response (Response[str]): The response containing the material ID. This ID can be used to fetch the material later.
        """
        ...

    async def on_chunk_read(
        self,
        response: Response[str | bytes | bytearray],
    ) -> None:
        """Called when a chunk of material has been read."""
        """
        Args:
            response (Response[str | bytes | bytearray]): The response containing the chunk data.
        """
        ...
