from __future__ import annotations
from typing import Protocol, Any, Sequence, Optional
from sbilifeco.models.base import Response
from pydantic import BaseModel
from datetime import datetime


class IDNameEntity(BaseModel):
    id: str
    name: str
    created_at: datetime
    updated_at: datetime = datetime.now()
    is_enabled: bool = True
    others: Optional[dict[str, Any]] = None

    def model_dump(self, **kwargs) -> dict[str, Any]:
        map = super().model_dump(**kwargs)
        map["created_at"] = self.created_at.isoformat()
        map["updated_at"] = self.updated_at.isoformat()
        return map


class IDNameRepoListener(Protocol):
    async def on_crupdate(self, request_id: str, response: Response[None]) -> None: ...
    async def on_delete(self, request_id: str, response: Response[None]) -> None: ...
    async def on_read_by_id(
        self, request_id: str, response: Response[IDNameEntity]
    ) -> None: ...
    async def on_read_many(
        self, request_id: str, response: Response[Sequence[IDNameEntity]]
    ) -> None: ...


class BaseIDNameRepo:
    def __init__(self) -> None:
        self.listeners: list[IDNameRepoListener] = []

    def add_listener(self, listener: IDNameRepoListener) -> BaseIDNameRepo:
        self.listeners.append(listener)
        return self

    async def crupdate(
        self, request_id: str, entity: IDNameEntity
    ) -> Response[None]: ...
    async def delete_by_id(self, request_id: str, entity_id: str) -> Response[None]: ...
    async def read_by_id(
        self, request_id: str, entity_id: str
    ) -> Response[IDNameEntity]: ...
    async def read_many(
        self, request_id: str, page_size: int = -1, page_num: int = -1
    ) -> Response[Sequence[IDNameEntity]]: ...
