from pydantic import BaseModel


class ToBertEmbeddingRequest(BaseModel):
    text: str


class ToBertEmbeddingResponse(BaseModel):
    embedding: list
