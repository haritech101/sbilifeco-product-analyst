from typing import Protocol
from sbilifeco.models.base import Response
from io import BufferedIOBase, RawIOBase, TextIOBase


class IngestFlow(Protocol):
    async def request_ingestion(self) -> Response[str]:
        """Request an ingestion operation."""
        """Returns: a response containing a service generated request ID"""
        ...

    async def ingest(
        self,
        ingestion_request: str,
        source: str | bytes | bytearray | TextIOBase | BufferedIOBase | RawIOBase,
    ) -> Response[None]:
        """Perform an ingestion operation."""
        """Args:
            ingestion_request: the request ID obtained from `request_ingestion`
            source: the data source to be ingested
        Returns: a response indicating success or failure of the ingestion"""
        ...


class IngestFlowListener(Protocol):
    async def on_request_ingestion(self, response: Response[str]) -> None:
        """Handle the event that a request for ingestion has been made."""
        """Args:
            response: the response containing the request ID or error information"""
        ...

    async def on_ingest(self, ingestion_request: str, response: Response[None]) -> None:
        """Handle the event that an ingestion operation has been performed."""
        """Args:
            ingestion_request: the request ID obtained from `request_ingestion`
            response: the response indicating success or failure of the ingestion"""
        ...
