from pydantic import BaseModel


class RecordMetadata(BaseModel):
    source_id: str
    source: str = ""
    chunk_num: int = 0


class VectorisedRecord(BaseModel):
    id: str
    document: str | bytes | None = None
    vector: list[int | float] = []
    metadata: RecordMetadata | None = None
    score: float = 0.0
