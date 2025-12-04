
create schema vkteams;

CREATE TABLE IF not exists vkteams.tasks 
(
    id      SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    vacancy_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP(0),
    vacancy_name    VARCHAR NOT NULL
);

CREATE TABLE IF not exists vkteams.users 
(
    id      SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    subscription_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP(0),
    vacancy    VARCHAR NOT NULL
    
);

CREATE TABLE IF not exists vkteams.calendar
(
    id      SERIAL PRIMARY KEY,
    VacancyId INTEGER NOT NULL,
    added_date TIMESTAMP NOT NULL,
    name_vacancy    VARCHAR  NOT NULL,
    categories    VARCHAR  NOT NULL,
    salary_min VARCHAR  NOT NULL,
    salary_max VARCHAR  NOT NULL,
    short_description    VARCHAR  NOT NULL,
    description    VARCHAR  NOT NULL,
    full_description    VARCHAR  NOT NULL,
    description_tsvector TSVECTOR,
    vip_status BOOLEAN NOT NULL DEFAULT FALSE,
    filter JSON


   
);