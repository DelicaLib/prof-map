import logging

import torch

from transformers import AutoTokenizer, AutoModel
from sklearn.cluster import DBSCAN
from dependencies.settings import Settings
from models.language_model import ClusteredSkills

LOGGER = logging.getLogger(__name__)


class RoBertaApplication:

    def __init__(self, settings: Settings):
        self._model_base_name = settings.bert.model
        self._model_skills_name = settings.bert.skills_model_path

        self._tokenizer_base = AutoTokenizer.from_pretrained(self._model_base_name)
        self._model_base = AutoModel.from_pretrained(self._model_base_name)

    async def _generate_skills_embeddings(self, skills: list[str]) -> list:
        inputs = self._tokenizer_base(skills, padding=True, truncation=True, return_tensors="pt", max_length=32)
        with torch.no_grad():
            outputs = self._model_base(**inputs)
            embeddings = outputs.last_hidden_state[:, 0, :]  # Используем CLS-токен

        return embeddings.numpy()

    async def _cluster_skills(self, skills: list[str], eps=0.0003, min_samples=1):
        skills = [skill.lower().strip() for skill in skills if len(skill) > 0]

        embeddings = await self._generate_skills_embeddings(skills)

        clustering = DBSCAN(eps=eps, min_samples=min_samples, metric="cosine").fit(embeddings)
        labels = clustering.labels_

        clusters = {}
        for skill, label in zip(skills, labels):
            if label == -1:
                label = "unclustered"
            clusters.setdefault(label, []).append(skill)

        return clusters

    async def _convert_clustered_skills(self, clustered):
        result_skills_dict = {}
        for cluster_id, clustered_skills in clustered.items():
            clustered_skills_set = set(clustered_skills)
            if len(clustered_skills_set) > 10:
                result_subclusters = await self._cluster_skills(
                    list(clustered_skills_set),
                    eps=0.0001
                )

                for subcluster_id, subclustered_skills in result_subclusters.items():
                    subclustered_skills_set = set(subclustered_skills)
                    if len(subclustered_skills_set) > 10:
                        for cur_skill in subclustered_skills_set:
                            result_skills_dict.setdefault(cur_skill, set())
                            result_skills_dict[cur_skill].add(cur_skill)
            else:
                cur_skill = sorted(list(clustered_skills_set))[0]
                result_skills_dict.setdefault(cur_skill, set())
                result_skills_dict[cur_skill].update(clustered_skills_set)
        return result_skills_dict

    async def get_clustered_skills(self, skills: list[str]) -> ClusteredSkills:
        result_clusters = await self._cluster_skills(skills)
        result_skills_dict = await self._convert_clustered_skills(result_clusters)
        return ClusteredSkills(
            clustered_skills=result_skills_dict,
            combined_skills=list(result_skills_dict.keys())
        )
