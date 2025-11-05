from pydantic import BaseModel


class RecordMetadata(BaseModel):
    source: str = ""
    chunk_num: int = 0


class VectorisedRecord(BaseModel):
    id: str
    document: str | bytes | None = None
    vector: list[int | float] = []
    metadata: RecordMetadata = RecordMetadata()
    score: float = 0.0
