from sbilifeco.boundaries.id_name_repo import (
    IDNameEntity as IDNameEntity,
    SortDirection as SortDirection,
    SortField as SortField,
)
from sbilifeco.cp.id_name_repo.paths import Pagination as Pagination


class IngestFlowPaths:
    BASE = "/api/v1/ingest-requests"
    BY_ID = BASE + "/{ingest_request_id}"  # POST

    MATERIALS = "/api/v1/material-list-requests"
