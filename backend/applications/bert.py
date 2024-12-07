import logging

import torch
import re

from transformers import BertTokenizer, BertModel, AutoModelForTokenClassification, AutoTokenizer
from dependencies.settings import Settings
from models.language_model import SkillsList

LOGGER = logging.getLogger(__name__)


class BertApplication:

    def __init__(self, settings: Settings):
        self._model_base_name = settings.bert.model
        self._model_skills_name = settings.bert.skills_model_path

        self._tokenizer_base = BertTokenizer.from_pretrained(self._model_base_name)
        self._model_base = BertModel.from_pretrained(self._model_base_name)

        self._model_skills_label = AutoModelForTokenClassification.from_pretrained(self._model_skills_name)
        self._tokenizer_skills_label = AutoTokenizer.from_pretrained(self._model_skills_name)

    async def get_bert_embedding(self, text: str) -> list:
        text = re.sub(r'[^\w\s]', ' ', text)
        inputs = self._tokenizer_base(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = self._model_base(**inputs)
        return outputs.last_hidden_state[:, 0, :].squeeze().detach().numpy().tolist()

    async def get_tokenized_text(self, text: str) -> list[str]:
        return self._tokenizer_base.tokenize(text)

    async def get_skills_from_text(self, text: str) -> SkillsList:
        tokens, predicted_labels = await self._predict_skill_labels(text, {2: 'O', 0: 'B-SKILL', 1: 'I-SKILL'})
        return SkillsList(skills=list(await self._merge_tokens(tokens, predicted_labels)))

    async def _predict_skill_labels(self, text: str, id_to_label: dict[int, str]) -> tuple[list[str], list[str]]:
        encoding = self._tokenizer_skills_label(text, return_tensors="pt", padding=True, truncation=True)

        with torch.no_grad():
            outputs = self._model_skills_label(**encoding)
        logits = outputs.logits
        predictions = torch.argmax(logits, dim=2)

        tokens = self._tokenizer_skills_label.convert_ids_to_tokens(encoding["input_ids"][0])
        predicted_labels = [id_to_label[pred.item()] for pred in predictions[0]]

        return tokens, predicted_labels

    @staticmethod
    async def _merge_tokens(tokens: list[str], labels: list[str]) -> set[str]:
        skills: list[str] = []
        current_label = ""
        last_label = ""
        current_word_to_merge: list[str] = []
        for token, label in zip(tokens, labels):
            if token.startswith("##"):
                current_word_to_merge.append(token[2:])
            else:
                current_word = "".join(current_word_to_merge)
                if current_word and current_label and current_label != 'O':
                    if current_label[0] == 'I' and last_label[1:] == current_label[1:]:
                        if not current_word.isalnum():
                            skills[-1] = skills[-1].strip()
                            skills[-1] = f"{skills[-1]}{current_word}"
                        else:
                            skills[-1] = f"{skills[-1]}{current_word} "
                    elif current_label[0] == 'I' and last_label[1:] != current_label[1:]:
                        LOGGER.warning(f"Last label '{last_label}' is not start for label '{current_label}'")
                    else:
                        skills.append(current_word)
                        if current_word.isalnum():
                            skills[-1] += " "
                current_word_to_merge = [token]
                last_label = current_label
                current_label = label

        current_word = "".join(current_word_to_merge)
        if current_word and current_label and current_label != 'O':
            if current_label[0] == 'I' and last_label[1:] == current_label[1:]:
                if not current_word.isalnum():
                    skills[-1] = skills[-1].strip()
                    skills[-1] = f"{skills[-1]}{current_word}"
                else:
                    skills[-1] = f"{skills[-1]}{current_word} "
            elif current_label[0] == 'I' and last_label[1:] != current_label[1:]:
                LOGGER.warning(f"Last label '{last_label}' is not start for label '{current_label}'")
            else:
                skills.append(current_word)
                if current_word.isalnum():
                    skills[-1] += " "
        return {skill.strip() for skill in skills}
