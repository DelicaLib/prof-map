from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from applications.bert import BertApplication
from models.language_model import ToBertEmbeddingResponse, TextRequest, SkillsList

language_model = APIRouter(prefix="/language_model", tags=["Language model"])


@language_model.post("/bert_embedding")
@inject
async def get_bert_embedding(
        request: TextRequest,
        *,
        bert_application: BertApplication = Depends(Provide['bert_application'])
) -> ToBertEmbeddingResponse:
    result = await bert_application.get_bert_embedding(request.text)
    return ToBertEmbeddingResponse(embedding=result)


@language_model.post("/text_to_skills")
@inject
async def get_skills_from_text(
        request: TextRequest,
        *,
        bert_application: BertApplication = Depends(Provide['bert_application'])
) -> SkillsList:
    result = await bert_application.get_skills_from_text(request.text)
    return result
