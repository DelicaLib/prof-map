import torch
import re

from transformers import BertTokenizer, BertModel
from dependencies.settings import Settings


class BertApplication:
    def __init__(self, settings: Settings):
        self._model_name = settings.bert.model
        self._tokenizer = BertTokenizer.from_pretrained(self._model_name)
        self._model = BertModel.from_pretrained(self._model_name)

    async def get_bert_embedding(self, text: str) -> list:
        text = re.sub(r'[^\w\s]', ' ', text)
        inputs = self._tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = self._model(**inputs)
        return outputs.last_hidden_state[:, 0, :].squeeze().detach().numpy().tolist()

