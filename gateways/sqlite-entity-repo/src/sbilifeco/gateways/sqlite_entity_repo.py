from __future__ import annotations
from re import S
from sqlite3 import Connection, connect, Row
from typing import Sequence
from json import dumps, loads
from sbilifeco.boundaries.id_name_repo import (
    BaseIDNameRepo,
    IDNameEntity,
    SortField,
    SortDirection,
)
from sbilifeco.models.base import Response


class SQLiteEntityRepo(BaseIDNameRepo):
    SQL_CREATE = (
        "create table if not exists "
        "entities("
        "id primary key on conflict replace, "
        "name not null unique on conflict replace, "
        "created_at not null, "
        "updated_at not null, "
        "is_enabled not null, "
        "others"
        ")"
    )
    SQL_INSERT = (
        "insert into "
        "entities(id, name, created_at, updated_at, is_enabled, others) "
        "values(:id, :name, :created_at, :updated_at, :is_enabled, :others)"
    )
    SQL_DELETE_BY_ID = "delete from entities where id = :entity_id"
    SQL_READ_BY_ID = "select * from entities where id = :entity_id"
    SQL_READ_MANY = "select * from entities"
    SQL_READ_MANY_PAGINATION = "limit :limit offset :offset"

    def __init__(self) -> None:
        super().__init__()
        self.path = ""
        self.connection: Connection

    def set_path(self, path: str) -> SQLiteEntityRepo:
        self.path = path
        return self

    async def async_init(self) -> None:
        self.connection = connect(self.path)
        self.connection.row_factory = Row
        self.connection.execute(self.SQL_CREATE)

    async def async_shutdown(self) -> None:
        self.connection.close()

    def _row_to_entity(self, row: Row) -> IDNameEntity:
        others = loads(row["others"])
        entity = IDNameEntity(
            id=row["id"],
            name=row["name"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            is_enabled=row["is_enabled"],
            others=others,
        )
        return entity

    async def crupdate(self, request_id: str, entity: IDNameEntity) -> Response[None]:
        try:
            values = entity.model_dump()
            values["others"] = dumps(values["others"])
            with self.connection:
                self.connection.execute(self.SQL_INSERT, {**values})
            return Response.ok(None)
        except Exception as e:
            return Response.error(e)

    async def delete_by_id(self, request_id: str, entity_id: str) -> Response[None]:
        try:
            with self.connection:
                self.connection.execute(self.SQL_DELETE_BY_ID, {"entity_id": entity_id})
            return Response.ok(None)
        except Exception as e:
            return Response.error(e)

    async def read_by_id(
        self, request_id: str, entity_id: str
    ) -> Response[IDNameEntity]:
        try:
            cursor = self.connection.execute(
                self.SQL_READ_BY_ID, {"entity_id": entity_id}
            )
            row = cursor.fetchone()
            if row is None:
                return Response.fail(f"Entity with ID {entity_id} is not found", 404)

            entity = self._row_to_entity(row)
            return Response.ok(entity)
        except Exception as e:
            return Response.error(e)

    async def read_many(
        self,
        request_id: str,
        page_size: int = -1,
        page_num: int = -1,
        sorts: dict[SortField, SortDirection] = {},
    ) -> Response[Sequence[IDNameEntity]]:
        try:
            limit = -1
            offset = -1
            if page_size > 0:
                limit = page_size
                page_num = page_num if page_num > 0 else 1
                offset = (page_num - 1) * page_size

            sql = f"{self.SQL_READ_MANY}"
            args = {}

            if sorts:
                sort_clauses = []
                for field, direction in sorts.items():
                    if field == SortField.NAME:
                        field_name = "name"
                    elif field == SortField.CREATED_AT:
                        field_name = "created_at"
                    elif field == SortField.UPDATED_AT:
                        field_name = "updated_at"
                    elif field == SortField.IS_ENABLED:
                        field_name = "is_enabled"
                    else:
                        continue  # Skip unsupported fields

                    sort_order = (
                        "ASC" if direction == SortDirection.ASCENDING else "DESC"
                    )
                    sort_clauses.append(f"{field_name} {sort_order}")

                if sort_clauses:
                    sql = f"{sql} ORDER BY {', '.join(sort_clauses)}"

            if limit > 0:
                sql = f"{sql} {self.SQL_READ_MANY_PAGINATION}"
                args["limit"] = limit
                args["offset"] = offset

            cursor = self.connection.execute(sql, args)
            rows = cursor.fetchall()
            entities = [self._row_to_entity(row) for row in rows]

            return Response.ok(entities)
        except Exception as e:
            return Response.error(e)
