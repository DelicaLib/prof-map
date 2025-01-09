import numpy as np
from keras import Model
from keras.src.saving import load_model
from keras.src.utils import pad_sequences
from tensorflow.keras.layers import Input, Embedding, LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.cluster import DBSCAN
import pandas as pd
import pickle


def save_model_and_mlb(model, mlb, model_path='./skills_prediction.keras', mlb_path='./mlb.pkl'):
    model.save(model_path)
    with open(mlb_path, 'wb') as f:
        pickle.dump(mlb, f)


def load_model_and_mlb(model_path='./skills_prediction.keras', mlb_path='./mlb.pkl'):
    model = load_model(model_path)
    with open(mlb_path, 'rb') as f:
        mlb = pickle.load(f)
    return model, mlb


def read_dataset(path: str):
    df = pd.read_csv(path, encoding='UTF-8')[:100]
    skills = list(df['skills'])
    skills_set = set()
    for skill in skills:
        skill_list = skill.strip('{}').replace("'", "").split(',')
        for s in skill_list:
            skills_set.add(s)

    return skills_set


def normalize_text(skill):
    return skill.lower().strip()


def generate_embeddings(skills, model_name="DeepPavlov/rubert-base-cased"):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    inputs = tokenizer(skills, padding=True, truncation=True, return_tensors="pt", max_length=32)

    with torch.no_grad():
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state[:, 0, :]  # Используем CLS-токен

    return embeddings.numpy()


def cluster_skills(skills, eps=0.5, min_samples=2, model_name="DeepPavlov/rubert-base-cased"):
    skills = [normalize_text(skill) for skill in skills if len(skill) > 0]

    embeddings = generate_embeddings(skills, model_name=model_name)

    clustering = DBSCAN(eps=eps, min_samples=min_samples, metric="cosine").fit(embeddings)
    labels = clustering.labels_

    clusters = {}
    for skill, label in zip(skills, labels):
        if label == -1:
            label = "unclustered"
        clusters.setdefault(label, []).append(skill)

    return clusters


def get_cluster_name(cluster_list):
    return sorted(list(cluster_list))[0]


def convert_clustered_skills(clustered, eps):
    result_skills_dict = {}
    for cluster_id, clustered_skills in clustered.items():
        clustered_skills_set = set(clustered_skills)
        if len(clustered_skills_set) > 10:
            result_subclusters = cluster_skills(list(clustered_skills_set), eps=eps - 0.0002, min_samples=1,
                                                model_name="FacebookAI/xlm-roberta-large")

            for subcluster_id, subclustered_skills in result_subclusters.items():
                subclustered_skills_set = set(subclustered_skills)
                if len(subclustered_skills_set) > 10:
                    for cur_skill in subclustered_skills_set:
                        result_skills_dict.setdefault(cur_skill, set())
                        result_skills_dict[cur_skill].add(cur_skill)
        else:
            cur_skill = get_cluster_name(clustered_skills_set)
            result_skills_dict.setdefault(cur_skill, set())
            result_skills_dict[cur_skill].update(clustered_skills_set)

    result = {}
    for skill_name, skill_group in result_skills_dict.items():
        for skill in skill_group:
            result[skill] = skill_name
    return result_skills_dict


def update_model_output_layer(model, num_classes):
    input_layer = model.input
    last_hidden_layer = model.layers[-2].output  # Последний скрытый слой перед выходом

    # Новый выходной слой с уникальным именем
    new_output_layer = Dense(num_classes, activation='sigmoid', name='new_dense_output')(last_hidden_layer)

    # Создаём обновлённую модель
    updated_model = Model(inputs=input_layer, outputs=new_output_layer)
    updated_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    return updated_model


def prepare_data_for_model(data, max_sequence_length=5, mlb=None):
    if mlb is None:
        mlb = MultiLabelBinarizer()
        binary_data = mlb.fit_transform(data)
    else:
        existing_classes = set(mlb.classes_)
        new_classes = set(label for sublist in data for label in sublist)
        all_classes = sorted(existing_classes.union(new_classes))  # Объединяем и сортируем классы
        mlb = MultiLabelBinarizer(classes=all_classes)
        binary_data = mlb.fit_transform(data)
    X, y = [], []
    for row in binary_data:
        indices = np.where(row == 1)[0]
        for i in range(1, len(indices)):
            X.append(indices[:i])
            y.append(row)

    X = pad_sequences(X, padding='post', maxlen=max_sequence_length)
    y = np.array(y)

    # Разделение данных на тренировочную и тестовую выборки
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test, mlb


def train_model(X_train, y_train, num_skills, embedding_dim=16, lstm_units=64, dense_units=128, epochs=10,
                batch_size=8, model=None):
    # Определение модели
    input_layer = Input(shape=(X_train.shape[1],))
    embedding_layer = Embedding(input_dim=num_skills, output_dim=embedding_dim, mask_zero=True)(input_layer)
    lstm_layer = LSTM(lstm_units, return_sequences=False)(embedding_layer)
    dense_layer = Dense(dense_units, activation='relu')(lstm_layer)
    dropout_layer = Dropout(0.2)(dense_layer)
    output_layer = Dense(num_skills, activation='sigmoid')(dropout_layer)

    if model is None:
        model = Model(inputs=input_layer, outputs=output_layer)
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    # Обучение модели
    model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_split=0.2)
    return model


def evaluate_model(model, X_test, y_test):
    loss, accuracy = model.evaluate(X_test, y_test)
    print(f"Test Accuracy: {accuracy:.2f}")
    return accuracy


def predict_skills(model, input_skills, mlb, k=3, max_sequence_length=5):
    # Преобразование входных навыков в числовую последовательность
    input_indices = [mlb.classes_.tolist().index(skill.lower().strip()) for skill in input_skills]
    input_sequence = pad_sequences([input_indices], padding='post', maxlen=max_sequence_length)

    # Предсказание вероятностей
    predictions = model.predict(input_sequence)[0]
    top_k_indices = predictions.argsort()[-k:][::-1]

    # Отбор навыков
    top_k_skills = [mlb.classes_[i] for i in top_k_indices if i not in input_indices]
    return input_skills + top_k_skills[:k]


def main():
    test_eps = 0.0003
    dataset_path = "IT_vacancies_for_prof_map.csv"
    # print("Reading dataset...")
    # skills_from_df = read_dataset(dataset_path)
    # print(f"initial len: {len(skills_from_df)}")
    #
    # print("Cluster skills...")
    # result_clusters = cluster_skills(
    #     list(skills_from_df),
    #     eps=test_eps,
    #     min_samples=1,
    #     model_name="FacebookAI/xlm-roberta-large"
    # )
    # result_skills = convert_clustered_skills(result_clusters, test_eps)
    #
    # print("Cluster end")
    #
    # for skill_name, clustered_skill in result_skills.items():
    #     if len(clustered_skill) > 1:
    #         print(f"Skill: {skill_name} (len: {len(clustered_skill)}) : {clustered_skill}")
    print("Reading dataset...")
    df = pd.read_csv(dataset_path, encoding='UTF-8')[60000:70000]
    print("Prepare data...")
    skills = list(df['skills'])
    skills_from_df = []
    for skill in skills:
        skill_list = skill.strip('{}').replace("'", "").split(',')
        skills_from_df.append(set())
        for cur_skill in skill_list:
                skills_from_df[-1].add(cur_skill.strip())
        skills_from_df[-1] = list(skills_from_df[-1])

    loaded_model, mlb = load_model_and_mlb()
    X_train, X_test, y_train, y_test, mlb = prepare_data_for_model(skills_from_df, mlb=mlb)

    print("Train model...")
    model = update_model_output_layer(loaded_model, y_train.shape[1])
    model = train_model(X_train, y_train, num_skills=y_train.shape[1], model=model)

    print("Ready!")

    # Оценка модели
    evaluate_model(model, X_test, y_test)
    # save_model_and_mlb(model, mlb)
    # loaded_model, mlb = load_model_and_mlb()
    input_skills = ["Python"]
    predicted_skills = predict_skills(model, input_skills, mlb, k=10)
    print("Input Skills:", input_skills)
    print("Predicted Skills:", predicted_skills)


if __name__ == "__main__":
    main()
