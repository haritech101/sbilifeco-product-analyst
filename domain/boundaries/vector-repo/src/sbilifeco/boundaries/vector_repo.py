from __future__ import annotations
from typing import Any, Protocol
from sbilifeco.models.base import Response
from sbilifeco.models.vectorisation import VectorisedRecord


class VectorRepoListener(Protocol): ...


class BaseVectorRepo:
    def __init__(self):
        self.listeners: list[VectorRepoListener] = []

    def add_listener(self, listener: VectorRepoListener) -> None:
        self.listeners.append(listener)

    async def crupdate(self, record: VectorisedRecord) -> Response[None]:
        raise NotImplementedError()

    async def delete_by_id(self, record_id: str) -> Response[None]:
        raise NotImplementedError()

    async def delete_by_criteria(self, criteria: dict[str, Any]) -> Response[None]:
        raise NotImplementedError()

    async def read_by_id(self, record_id: str) -> Response[VectorisedRecord]:
        raise NotImplementedError()

    async def read_by_criteria(
        self, criteria: dict[str, Any]
    ) -> Response[list[VectorisedRecord]]:
        raise NotImplementedError()
