from __future__ import annotations
from typing import Protocol
from sbilifeco.models.base import Response
from pydantic import BaseModel


class RatedAnswer(BaseModel):
    answer: str
    rating: float


class BaseQueryFlow:
    def __init__(self) -> None:
        self.listeners: list[IQueryFlowListener] = []

    def add_listener(self, listener: IQueryFlowListener) -> None:
        """Add a listener to the QueryFlow."""
        self.listeners.append(listener)

    async def request_search(self) -> Response[str]:
        """Request a search request ID for performing queries."""
        ...

    async def search(
        self, search_request_id: str, query: str, num_results: int = 5
    ) -> Response[list[RatedAnswer]]:
        """Perform a search based on the provided query and return a list of rated answers."""
        """
        Args:
            search_request_id: the ID used to identify the search request
            query: the search query string
        Returns:
            A Response object containing a list of RatedAnswer or error information. The list is sorted by rating in descending order.
        """
        ...


class IQueryFlowListener(Protocol):
    async def on_request_search(self, response: Response[str]) -> None:
        """Handle the event that a search request ID has been obtained."""
        """Args:
            response: the response containing the search request ID or error information"""
        ...

    async def on_search(self, response: Response[list[RatedAnswer]]) -> None:
        """Handle the event that a search has been performed."""
        """Args:
            response: the response containing the list of rated answers or error information"""
        ...
