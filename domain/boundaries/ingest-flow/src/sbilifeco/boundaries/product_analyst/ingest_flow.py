from __future__ import annotations
from typing import Protocol
from sbilifeco.models.base import Response
from io import BufferedIOBase, RawIOBase, TextIOBase
from sbilifeco.boundaries.id_name_repo import IDNameEntity, SortField, SortDirection


class BaseIngestFlow:
    def __init__(self) -> None:
        self.listeners: list[IngestFlowListener] = []

    def add_listener(self, listener: IngestFlowListener) -> None:
        """Add a listener to the ingest flow."""
        """Args:
            listener: an instance of IngestFlowListener to be added"""
        self.listeners.append(listener)

    async def request_ingestion(self) -> Response[str]:
        """Request an ingestion operation."""
        """Returns: a response containing a service generated request ID"""
        ...

    async def ingest(
        self,
        ingestion_request: str,
        title: str,
        source: str | bytes | bytearray | TextIOBase | BufferedIOBase | RawIOBase,
    ) -> Response[None]:
        """Perform an ingestion operation."""
        """Args:
            ingestion_request: the request ID obtained from `request_ingestion`
            source: the data source to be ingested
        Returns: a response indicating success or failure of the ingestion"""
        ...

    async def get_materials(
        self,
        page_size: int = -1,
        page: int = -1,
        sorts: dict[SortField, SortDirection] = {},
    ) -> Response[list[IDNameEntity]]:
        """Retrieve a list of ingested materials."""
        """Args:
            page_size: number of items per page
            page: page number to retrieve. Start from 1 and not 0
        Returns: a response containing a list of material identifiers and names"""
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
