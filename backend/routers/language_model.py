from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from applications import RoBertaApplication
from applications.bert import BertApplication
from models.language_model import ToBertEmbeddingResponse, TextRequest, SkillsList, ClusteredSkills, SkillsListRequest

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
    result = await bert_application.get_clustered_skills_from_text(request.text)
    return result


@language_model.post("/cluster_skills")
@inject
async def cluster_skills(
        skills: SkillsListRequest,
        *,
        roberta_application: RoBertaApplication = Depends(Provide['roberta_application'])
) -> ClusteredSkills:
    result = await roberta_application.get_clustered_skills(skills.skills)
    return result
