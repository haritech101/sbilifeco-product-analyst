from __future__ import annotations

from io import BufferedIOBase, RawIOBase, TextIOBase
from uuid import uuid4
from typing import Any
from datetime import datetime

from sbilifeco.boundaries.material_reader import BaseMaterialReader
from sbilifeco.boundaries.product_analyst.ingest_flow import BaseIngestFlow
from sbilifeco.boundaries.vector_repo import BaseVectorRepo
from sbilifeco.boundaries.vectoriser import BaseVectoriser
from sbilifeco.boundaries.id_name_repo import BaseIDNameRepo, IDNameEntity
from sbilifeco.models.base import Response
from sbilifeco.models.vectorisation import VectorisedRecord, RecordMetadata


class IngestFlow(BaseIngestFlow):
    def __init__(self) -> None:
        super().__init__()
        self.ingestion_requests: dict[str, Any] = {}
        self.material_reader: BaseMaterialReader
        self.vectoriser: BaseVectoriser
        self.vector_repo: BaseVectorRepo
        self.id_name_repo: BaseIDNameRepo

    def set_material_reader(self, material_reader: BaseMaterialReader) -> IngestFlow:
        self.material_reader = material_reader
        return self

    def set_vectoriser(self, vectoriser: BaseVectoriser) -> IngestFlow:
        self.vectoriser = vectoriser
        return self

    def set_vector_repo(self, vector_repo: BaseVectorRepo) -> IngestFlow:
        self.vector_repo = vector_repo
        return self

    def set_id_name_repo(self, id_name_repo: BaseIDNameRepo) -> IngestFlow:
        self.id_name_repo = id_name_repo
        return self

    async def async_init(self) -> None: ...

    async def async_shutdown(self) -> None: ...

    async def request_ingestion(self) -> Response[str]:
        try:
            request_id = str(uuid4())
            self.ingestion_requests[request_id] = None
            return Response.ok(request_id)
        except Exception as e:
            return Response.error(e)

    async def ingest(
        self,
        ingestion_request: str,
        title: str,
        source: str | bytes | bytearray | TextIOBase | BufferedIOBase | RawIOBase,
    ) -> Response[None]:
        try:
            # Read from source
            print("Ask material reader to read from source")
            read_response = await self.material_reader.read_material(source)
            if not read_response.is_success:
                print(f"Error while reading material: {read_response.message}")
                return Response.fail(read_response.message, read_response.code)
            elif read_response.payload is None:
                return Response.fail("Material ID is inexplicably empty", 500)
            material_id = read_response.payload

            source_id = uuid4().hex

            entity_request_id = uuid4().hex
            entity = IDNameEntity(id=source_id, name=title, created_at=datetime.now())

            print(f"Mark an entry to map ID {source_id} to name {title}")
            entity_response = await self.id_name_repo.crupdate(
                entity_request_id, entity
            )
            if not entity_response.is_success:
                print(
                    f"Error while creating ID-name mapping: {entity_response.message}"
                )
                return Response.fail(entity_response.message, entity_response.code)

            are_chunks_left = True
            chunk_num = 0

            while are_chunks_left:
                print(
                    f"Chunks are left to read, ask material reader for chunk {chunk_num}"
                )
                chunk_response = await self.material_reader.read_next_chunk(material_id)
                if not chunk_response.is_success:
                    print(
                        f"Error while reading chunk {chunk_num}: {chunk_response.message}"
                    )
                    return Response.fail(chunk_response.message, chunk_response.code)
                elif chunk_response.payload is None:
                    print("No more chunks left")
                    are_chunks_left = False
                    continue

                print(f"Chunk {chunk_num} read")
                chunk = chunk_response.payload

                vectorise_request_id = uuid4().hex
                print(f"Ask vectoriser to vectorise chunk {chunk_num}")
                vector_response = await self.vectoriser.vectorise(
                    vectorise_request_id, chunk
                )
                if not vector_response.is_success:
                    print(
                        f"Error while vectorising chunk {chunk_num}: {vector_response.message}"
                    )
                    return Response.fail(vector_response.message, vector_response.code)
                elif vector_response.payload is None:
                    return Response.fail("Vector is inexplicably empty", 500)

                print(f"Chunk {chunk_num} vectorised")
                vector = vector_response.payload

                record_id = uuid4().hex

                record = VectorisedRecord(
                    id=record_id,
                    vector=vector,
                    document=chunk,
                    metadata=RecordMetadata(
                        source_id=source_id, chunk_num=chunk_num, source=title
                    ),
                )

                print(f"Ask vector repo to store vector for chunk {chunk_num}")
                crupdate_response = await self.vector_repo.crupdate(record)
                if not crupdate_response.is_success:
                    print(
                        f"Error while storing vector for chunk {chunk_num}: {crupdate_response.message}"
                    )
                    return Response.fail(
                        crupdate_response.message, crupdate_response.code
                    )
                print(f"Chunk {chunk_num} vector stored in vector repo")

                chunk_num += 1

            print("Ingestion completed successfully")
            return Response.ok(None)
        except Exception as e:
            return Response.error(e)
