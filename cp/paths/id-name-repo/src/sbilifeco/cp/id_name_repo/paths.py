from typing import Any, Callable, Literal, Optional
from pydantic import BaseModel
from sbilifeco.boundaries.id_name_repo import IDNameEntity, SortField, SortDirection


class Pagination(BaseModel):
    page_size: int = -1
    page_num: int = -1
    sorts: dict[SortField, SortDirection] = {}


class IDNameOp(BaseModel):
    request_id: str
    params: Optional[IDNameEntity | str | Pagination] = None

    def model_dump(self, **kwargs) -> dict[str, Any]:
        dump = super().model_dump(**kwargs)
        if isinstance(self.params, IDNameEntity):
            dump["params"] = self.params.model_dump()

        return dump


class Paths:
    BASE = "/api/v1/id-name-entities"
    UPSERT_REQUESTS = BASE + "/upsert-requests"
    DELETE_REQUESTS = BASE + "/delete-requests"
    READ_BY_ID_REQUESTS = BASE + "/read-by-id-requests"
    READ_MANY_REQUESTS = BASE + "/read-many-requests"
