from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from applications.bert import BertApplication
from models.language_model import ToBertEmbeddingResponse, ToBertEmbeddingRequest

language_model = APIRouter(prefix="/language_model")


@language_model.post("/bert_embedding")
@inject
async def get_bert_embedding(
        request: ToBertEmbeddingRequest,
        *,
        bert_application: BertApplication = Depends(Provide['bert_application'])
) -> ToBertEmbeddingResponse:
    result = await bert_application.get_bert_embedding(request.text)
    return ToBertEmbeddingResponse(embedding=result)
