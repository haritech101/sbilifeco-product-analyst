from typing import Protocol
from sbilifeco.models.base import Response
from io import BufferedIOBase, RawIOBase, TextIOBase


class IngestFlow(Protocol):
    async def ingest(
        self, source: str | bytes | bytearray | TextIOBase | BufferedIOBase | RawIOBase
    ) -> Response[None]: ...
