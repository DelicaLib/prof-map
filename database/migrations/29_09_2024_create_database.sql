CREATE DATABASE prof_map;

CREATE TABLE vacancy (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(256) NOT NULL
);

CREATE TABLE skill (
    id SERIAL PRIMARY KEY,
    name VARCHAR(256) NOT NULL
);

CREATE TABLE vacancy_skill (
    vacancy_id BIGINT REFERENCES vacancy(id) ON DELETE CASCADE,
    skill_id BIGINT REFERENCES skill(id) ON DELETE CASCADE,
    PRIMARY KEY (vacancy_id, skill_id)
);

CREATE VIEW vacancy_skill_view AS
SELECT
    vacancy.id,
    vacancy.name,
    array_agg(skill.name) AS skills
FROM
    vacancy
LEFT JOIN
    vacancy_skill ON vacancy.id = vacancy_skill.vacancy_id
LEFT JOIN
    skill ON vacancy_skill.skill_id = skill.id
GROUP BY
    vacancy.id, vacancy.name;
