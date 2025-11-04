from __future__ import annotations
from sbilifeco.models.base import Response
from sbilifeco.boundaries.vectoriser import BaseVectoriser
from chromadb.api import ClientAPI
from chromadb import PersistentClient
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction


class FileSystemChromDB(BaseVectoriser):
    def __init__(self):
        super().__init__()
        self.db_path = ""
        self.chroma_client: ClientAPI
        self.embedding_function: DefaultEmbeddingFunction

    def set_db_path(self, db_path: str) -> FileSystemChromDB:
        self.db_path = db_path
        return self

    async def async_init(self) -> None:
        self.chroma_client = PersistentClient(path=self.db_path)
        self.embedding_function = DefaultEmbeddingFunction()

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
