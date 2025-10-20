from typing import Protocol
from sbilifeco.models.base import Response
from pydantic import BaseModel


class RatedAnswer(BaseModel):
    answer: str
    rating: float


class IQueryFlow(Protocol):
    async def search(self, query: str) -> Response[list[RatedAnswer]]:
        """Perform a search based on the provided query and return a list of rated answers."""
        """The list is sorted by rating in descending order."""
        ...


class QueryFlowListener(Protocol):
    async def on_search(self, response: Response[list[RatedAnswer]]) -> None: ...
