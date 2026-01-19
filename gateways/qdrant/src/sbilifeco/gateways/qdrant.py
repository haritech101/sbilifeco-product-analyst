from __future__ import annotations
from typing import Any
from pprint import pformat
from sbilifeco.models.base import Response

# Import other required contracts/modules here
from uuid import UUID
from fastembed import TextEmbedding
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    PointStruct,
    Distance,
    VectorParams,
    UpdateStatus,
    Filter,
    FieldCondition,
    MatchValue,
    Record,
    ScoredPoint,
)
from qdrant_client.http.exceptions import UnexpectedResponse
from sbilifeco.boundaries.vector_repo import BaseVectorRepo
from sbilifeco.boundaries.vectoriser import BaseVectoriser
from sbilifeco.models.vectorisation import VectorisedRecord, RecordMetadata


class QdrantGateway(BaseVectoriser, BaseVectorRepo):
    def __init__(self):
        self.qd: AsyncQdrantClient
        self.url: str
        self.collection_name: str

    def set_url(self, url: str) -> QdrantGateway:
        self.url = url
        return self

    def set_collection_name(self, collection_name: str) -> QdrantGateway:
        self.collection_name = collection_name
        return self

    async def async_init(self, **kwargs) -> None:
        self.qd = AsyncQdrantClient(url=f"{self.url}")
        self.embedder = TextEmbedding()

        if not (await self.qd.collection_exists(collection_name=self.collection_name)):
            await self.qd.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedder.embedding_size, distance=Distance.COSINE
                ),
            )

    async def async_shutdown(self, **kwargs) -> None:
        await self.qd.close()

    async def vectorise(
        self, request_id: str, material: str | bytes | bytearray
    ) -> Response[list[float | int]]:
        try:
            material_as_text = ""
            if isinstance(material, (bytes, bytearray)):
                material_as_text = material.decode("utf-8")
            elif isinstance(material, str):
                material_as_text = material

            vector = list(self.embedder.embed(material_as_text))[0].tolist()
            return Response.ok(vector)
        except Exception as e:
            return Response.error(e)

    async def crupdate(self, record: VectorisedRecord) -> Response[None]:
        try:
            payload: dict[str, Any] = {"document": record.document}
            if record.metadata:
                payload["metadata"] = record.metadata.model_dump()

            point = PointStruct(
                id=record.id,
                vector=record.vector,
                payload=payload,
            )
            result = await self.qd.upsert(self.collection_name, [point])
            if result.status != UpdateStatus.COMPLETED:
                return Response.fail(f"Upsert not completed: {pformat(result)}")

            return Response.ok(None)
        except UnexpectedResponse as e:
            return Response.fail(e.content.decode("utf-8"))
        except Exception as e:
            return Response.error(e)

    async def read_by_id(self, record_id: str) -> Response[VectorisedRecord]:
        try:
            result = await self.qd.retrieve(
                collection_name=self.collection_name, ids=[record_id]
            )
            if not result:
                return Response.fail(f"Record with ID {record_id} not found", 404)
            point = result[0]

            if not point:
                return Response.fail(
                    f"Record with ID {record_id} is inexplicably blank"
                )

            vectorised_record = self.__model_from_record(point)

            return Response.ok(vectorised_record)
        except Exception as e:
            return Response.error(e)

    async def delete_by_id(self, record_id: str) -> Response[None]:
        try:
            result = await self.qd.delete(self.collection_name, [record_id])
            if result.status != UpdateStatus.COMPLETED:
                return Response.fail(f"Delete not completed: {pformat(result)}")

            return Response.ok(None)
        except Exception as e:
            return Response.error(e)

    async def read_by_criteria(
        self, criteria: dict[str, Any]
    ) -> Response[list[VectorisedRecord]]:
        try:
            filter = self.__filter_from_criteria(criteria)

            result = await self.qd.scroll(
                collection_name=self.collection_name,
                scroll_filter=filter,
            )
            records = result[0]

            return Response.ok([self.__model_from_record(record) for record in records])
        except Exception as e:
            return Response.error(e)

    async def delete_by_criteria(self, criteria: dict[str, Any]) -> Response[None]:
        try:
            filter = self.__filter_from_criteria(criteria)

            result = await self.qd.delete(
                collection_name=self.collection_name,
                points_selector=filter,
            )
            if result.status != UpdateStatus.COMPLETED:
                return Response.fail(f"Delete not completed: {pformat(result)}")

            return Response.ok(None)
        except Exception as e:
            return Response.error(e)

    async def search_by_vector(
        self, vector: list[float], num_results: int = 5
    ) -> Response[list[VectorisedRecord]]:
        try:
            result = await self.qd.query_points(
                self.collection_name, vector, limit=num_results
            )
            if not result.points:
                return Response.ok([])

            return Response.ok(
                [self.__model_from_record(point) for point in result.points]
            )
        except Exception as e:
            return Response.error(e)

    def __model_from_record(self, record: Record | ScoredPoint) -> VectorisedRecord:
        retrieved_record_id = ""
        if isinstance(record.id, UUID):
            retrieved_record_id = record.id.hex.replace("-", "")
        elif isinstance(record.id, str):
            retrieved_record_id = record.id.replace("-", "")
        else:
            retrieved_record_id = str(record.id)

        vectorised_record = VectorisedRecord(
            id=retrieved_record_id,
            document=record.payload.get("document", "") if record.payload else "",
            metadata=RecordMetadata.model_validate(
                record.payload.get("metadata", {}) if record.payload else {}
            ),
            vector=[],
            score=getattr(record, "score", 0.0),
        )

        return vectorised_record

    def __filter_from_criteria(self, criteria: dict[str, Any]) -> Filter:
        return Filter(
            must=[
                FieldCondition(key=f"metadata.{key}", match=MatchValue(value=value))
                for key, value in criteria.items()
            ]
        )
