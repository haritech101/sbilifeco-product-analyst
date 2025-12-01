from __future__ import annotations
from typing import Any
from sbilifeco.models.base import Response
from sbilifeco.boundaries.vectoriser import BaseVectoriser
from sbilifeco.boundaries.vector_repo import BaseVectorRepo
from chromadb.api import ClientAPI
from chromadb import PersistentClient
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from sbilifeco.models.vectorisation import VectorisedRecord, RecordMetadata


class FileSystemChromDB(BaseVectoriser, BaseVectorRepo):
    def __init__(self):
        BaseVectoriser.__init__(self)
        BaseVectorRepo.__init__(self)
        self.db_path = ""
        self.chroma_client: ClientAPI
        self.embedding_function: DefaultEmbeddingFunction

    def set_db_path(self, db_path: str) -> FileSystemChromDB:
        self.db_path = db_path
        return self

    def set_collection_name(self, collection_name: str) -> FileSystemChromDB:
        self.collection_name = collection_name
        return self

    async def async_init(self) -> None:
        self.chroma_client = PersistentClient(path=self.db_path)
        self.embedding_function = DefaultEmbeddingFunction()
        self.chroma_client.get_or_create_collection(self.collection_name)

    async def async_shutdown(self) -> None: ...

    async def vectorise(
        self, request_id: str, material: str | bytes | bytearray
    ) -> Response[list[float | int]]:
        try:
            material_as_str = ""

            if isinstance(material, str):
                material_as_str = material
            if isinstance(material, (bytes, bytearray)):
                material_as_str = material.decode("utf-8")

            embeddings = self.embedding_function([material_as_str])

            return Response.ok(embeddings[0].tolist())
        except Exception as e:
            return Response.error(e)

    async def crupdate(self, record: VectorisedRecord) -> Response[None]:
        try:
            # Adjust
            document_as_str = ""
            if isinstance(record.document, str):
                document_as_str = record.document
            if isinstance(record.document, (bytes, bytearray)):
                document_as_str = record.document.decode("utf-8")

            # Upsert
            self.chroma_client.get_collection(self.collection_name).upsert(
                ids=[record.id],
                documents=[document_as_str],
                embeddings=[record.vector],
                metadatas=[record.metadata.model_dump()],
            )

            # Return
            return Response.ok(None)
        except Exception as e:
            return Response.error(e)

    async def delete_by_id(self, record_id: str) -> Response[None]:
        try:
            # Delete
            self.chroma_client.get_collection(self.collection_name).delete(
                ids=[record_id]
            )

            # Return
            return Response.ok(None)
        except Exception as e:
            return Response.error(e)

    async def delete_by_criteria(self, criteria: dict[str, Any]) -> Response[None]:
        try:
            # Delete
            self.chroma_client.get_collection(self.collection_name).delete(
                where=criteria
            )

            # Return
            return Response.ok(None)
        except Exception as e:
            return Response.error(e)

    async def read_by_id(self, record_id: str) -> Response[VectorisedRecord]:
        try:
            # Fetch
            query_result = self.chroma_client.get_collection(self.collection_name).get(
                ids=[record_id], include=["documents", "metadatas"]
            )

            # Validate
            if not query_result["ids"]:
                return Response.fail(f"Record with ID {record_id} not found.", 404)
            if "documents" not in query_result or not query_result["documents"]:
                return Response.fail(
                    f"For record {record_id}, document content is inexplicably empty"
                )
            if "metadatas" not in query_result or not query_result["metadatas"]:
                return Response.fail(
                    f"For record {record_id}, metadata is inexplicably empty"
                )

            # Triage
            record = VectorisedRecord(
                id=query_result["ids"][0],
                vector=[],
                metadata=RecordMetadata.model_validate(query_result["metadatas"][0]),
                document=query_result["documents"][0],
            )

            # Return
            return Response.ok(record)
        except Exception as e:
            return Response.error(e)

    async def read_by_criteria(
        self, criteria: dict[str, Any]
    ) -> Response[list[VectorisedRecord]]:
        # Fetch
        query_result = self.chroma_client.get_collection(self.collection_name).get(
            where=criteria, include=["documents", "metadatas"]
        )

        # Validate
        if not query_result["ids"]:
            return Response.fail(f"Record with criteria {criteria} not found.", 404)
        if "documents" not in query_result or not query_result["documents"]:
            return Response.fail(
                f"For record with criteria {criteria}, document content is inexplicably empty"
            )
        if "metadatas" not in query_result or not query_result["metadatas"]:
            return Response.fail(
                f"For record with criteria {criteria}, metadata is inexplicably empty"
            )

        # Triage
        records = [
            VectorisedRecord(
                id=query_result["ids"][i],
                vector=[],
                metadata=RecordMetadata.model_validate(
                    query_result["metadatas"][i]
                    if "metadatas" in query_result and query_result["metadatas"]
                    else {}
                ),
                document=(
                    query_result["documents"][i]
                    if "documents" in query_result and query_result["documents"]
                    else ""
                ),
            )
            for i in range(len(query_result["ids"]))
        ]

        # Return
        return Response.ok(records)

    async def search_by_vector(
        self, vector: list[float], num_results: int = 5
    ) -> Response[list[VectorisedRecord]]:
        try:
            # Fetch
            query_result = self.chroma_client.get_collection(
                self.collection_name
            ).query(
                query_embeddings=[vector],
                n_results=num_results,
                include=["documents", "metadatas", "distances"],
            )

            # Validate
            if not query_result["ids"]:
                return Response.fail("No semantically matching records found.", 404)

            # Triage
            records = [
                VectorisedRecord(
                    id=query_result["ids"][0][i],
                    vector=[],
                    metadata=RecordMetadata.model_validate(
                        query_result["metadatas"][0][i]
                        if "metadatas" in query_result and query_result["metadatas"]
                        else {}
                    ),
                    document=(
                        query_result["documents"][0][i]
                        if "documents" in query_result and query_result["documents"]
                        else ""
                    ),
                    score=(
                        query_result["distances"][0][i]
                        if "distances" in query_result and query_result["distances"]
                        else 0.0
                    ),
                )
                for i in range(len(query_result["ids"][0]))
            ]

            # Return
            return Response.ok(records)
        except Exception as e:
            return Response.error(e)
