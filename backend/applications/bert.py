import logging

import torch
import re
import nltk
import spacy

from dependency_injector.wiring import Provide
from nltk import SnowballStemmer
from transformers import BertTokenizer, BertModel, AutoModelForTokenClassification, AutoTokenizer

from applications.roberta import RoBertaApplication
from dependencies.settings import Settings
from models.language_model import SkillsList

LOGGER = logging.getLogger(__name__)


class BertApplication:

    _SPECIAL_CHARACTERS: list[str] = [
        "!", "@", "$", "%", "^", "&", "*", "(", ")", "-", "_", "=",
        "{", "}", "[", "]", "|", "\\", ":", ";", "'", "\"", "<", ">", ",", ".",
        "?", "/", "~", "`", " "
    ]

    def __init__(self, settings: Settings):
        nltk.download('punkt')
        self._russian_stemmer = SnowballStemmer("russian")
        self._nlp = spacy.load("en_core_web_sm")
        self._model_base_name = settings.bert.model
        self._model_skills_name = settings.bert.skills_model_path

        self._tokenizer_base = BertTokenizer.from_pretrained(self._model_base_name)
        self._model_base = BertModel.from_pretrained(self._model_base_name)

        self._model_skills_label = AutoModelForTokenClassification.from_pretrained(self._model_skills_name)
        self._tokenizer_skills_label = AutoTokenizer.from_pretrained(self._model_skills_name)

    def _split_into_chunks(self, text: str, chunk_size: int = 512) -> list:
        tokens = self._tokenizer_base.encode(text, add_special_tokens=True)
        chunks = [tokens[i:i + chunk_size] for i in range(0, len(tokens), chunk_size)]
        return [self._tokenizer_base.decode(chunk) for chunk in chunks]

    async def get_bert_embedding(self, text: str) -> list:
        text = re.sub(r'[^\w\s]', ' ', text)
        chunks = self._split_into_chunks(text, chunk_size=510)
        embeddings = []
        for chunk in chunks:
            inputs = self._tokenizer_base(chunk, return_tensors='pt', truncation=True, padding=True, max_length=512)
            with torch.no_grad():
                outputs = self._model_base(**inputs)
            embeddings.append(outputs.last_hidden_state[:, 0, :].squeeze().detach().numpy().tolist())
        return embeddings

    async def get_tokenized_text(self, text: str) -> list[str]:
        return self._tokenizer_base.tokenize(text)

    async def get_clustered_skills_from_text(
            self,
            text: str,
            *,
            roberta_application: RoBertaApplication = Provide['roberta_application']
    ) -> SkillsList:
        tokens, predicted_labels = await self._predict_skill_labels(
            text,
            {2: 'O', 0: 'B-SKILL', 1: 'I-SKILL'}
        )
        skills = list(await self._merge_tokens(tokens, predicted_labels))
        clustered_skills = await roberta_application.get_clustered_skills(skills)
        return SkillsList(
            skills=skills,
            clustered=clustered_skills
        )

    async def get_skills_from_text(
            self,
            text: str,
    ) -> SkillsList:
        tokens, predicted_labels = await self._predict_skill_labels(
            text,
            {2: 'O', 0: 'B-SKILL', 1: 'I-SKILL'}
        )
        skills = list(await self._merge_tokens(tokens, predicted_labels))
        return SkillsList(
            skills=skills,
            clustered=None
        )

    async def _predict_skill_labels(self, text: str, id_to_label: dict[int, str]) -> tuple[list[str], list[str]]:
        chunks = self._split_into_chunks(text, chunk_size=500)
        all_logits = []
        for chunk in chunks:
            encoding = self._tokenizer_skills_label(chunk, return_tensors="pt", padding=True, truncation=True)
            with torch.no_grad():
                outputs = self._model_skills_label(**encoding)
            all_logits.append(outputs.logits)

        logits = torch.cat(all_logits, dim=1)
        predictions = torch.argmax(logits, dim=2)

        tokens = self._tokenizer_skills_label.convert_ids_to_tokens(encoding["input_ids"][0])
        predicted_labels = [id_to_label[pred.item()] for pred in predictions[0]]

        return tokens, predicted_labels

    async def _merge_tokens(self, tokens: list[str], labels: list[str]) -> set[str]:
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
                        if len(skills) == 0:
                            skills.append("")
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
        return {
            skill.strip("".join(self._SPECIAL_CHARACTERS))
            for skill in skills
            if not (len(skill) == 1 and not skill[0].isalpha())
        }

    async def normalize_word(self, word: str):
        word = word.lower().strip()

        if word.isalpha() and any('а' <= c <= 'я' for c in word):
            return self._russian_stemmer.stem(word)
        elif word.isalpha() and any('a' <= c <= 'z' for c in word):
            doc = self._nlp(word)
            return doc[0].lemma_
        return word

