ALTER TABLE vacancy
    ADD COLUMN hh_id bigint;

CREATE UNIQUE INDEX idx_vacancy_hh_id
    ON vacancy (hh_id);

CREATE UNIQUE INDEX idx_skill_name
    ON skill (name);
