import os
import torch
from transformers import Trainer, TrainingArguments, AutoTokenizer, AutoModelForTokenClassification
from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split
import numpy as np
from seqeval.metrics import classification_report

# Загрузка данных
conll_file_path = "C:\\Users\\danil\\Downloads\\project-1-at-2024-11-03-14-58-1db74424.conll"


# Функция для чтения данных в формате CoNLL
def read_conll_file(file_path):
    sentences = []
    labels = []
    words = []
    tags = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "":
                if words:
                    sentences.append(words)
                    labels.append(tags)
                    words = []
                    tags = []
            else:
                parts = line.split()
                if len(parts) > 1:
                    words.append(parts[0])
                    tags.append(parts[-1])
    return sentences, labels


# Чтение файла
sentences, labels = read_conll_file(conll_file_path)

# Создание уникальных меток
unique_labels = sorted(set(tag for doc in labels for tag in doc))
label2id = {label: i for i, label in enumerate(unique_labels)}
id2label = {i: label for label, i in label2id.items()}

# Преобразование меток в индексы
labels = [[label2id[label] for label in doc] for doc in labels]

# Разделение на обучающую и тестовую выборки
train_texts, val_texts, train_labels, val_labels = train_test_split(
    sentences,
    labels,
    test_size=0.2
)

# Инициализация токенизатора BERT
tokenizer = AutoTokenizer.from_pretrained("DeepPavlov/rubert-base-cased", add_prefix_space=True)


# Создание кастомного Dataset для работы с токенами
class NERDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        labels = self.labels[idx]

        encoding = self.tokenizer(text,
                                  is_split_into_words=True,
                                  padding="max_length",
                                  truncation=True,
                                  max_length=self.max_length)

        # Создание меток для каждого токена
        label_ids = [-100] * len(encoding["input_ids"])
        word_ids = encoding.word_ids()

        for i, word_id in enumerate(word_ids):
            if word_id is None:
                continue
            label_ids[i] = labels[word_id] if word_id < len(labels) else -100

        encoding["labels"] = label_ids
        return {key: torch.tensor(val) for key, val in encoding.items()}


# Создание датасетов
train_dataset = NERDataset(train_texts, train_labels, tokenizer)
val_dataset = NERDataset(val_texts, val_labels, tokenizer)

# Инициализация модели BERT для классификации токенов
model = AutoModelForTokenClassification.from_pretrained("DeepPavlov/rubert-base-cased", num_labels=len(unique_labels))

# Параметры обучения
training_args = TrainingArguments(
    output_dir="./results2",
    eval_strategy="epoch",
    learning_rate=5e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=5,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=100,
)

# Определение Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    tokenizer=tokenizer,
)

# Запуск обучения
trainer.train()

# Оценка модели
predictions, labels, _ = trainer.predict(val_dataset)
preds = np.argmax(predictions, axis=2)

# Удаление -100 и преобразование меток в исходные
true_labels = [[id2label[label] for label in label_seq if label != -100] for label_seq in labels]
true_preds = [[id2label[pred] for pred, label in zip(pred_seq, label_seq) if label != -100] for pred_seq, label_seq in
              zip(preds, labels)]

# Вывод отчета классификации
print(classification_report(true_labels, true_preds))

trainer.save_model("./skills_label_model")  # сохраняет модель, конфигурацию и токенизатор
tokenizer.save_pretrained("./skills_label_model")  # сохраняет токенизатор
