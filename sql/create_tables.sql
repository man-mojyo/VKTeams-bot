
create schema vkteams;

CREATE TABLE IF not exists vkteams.tasks 
(
    id      SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    task_name    VARCHAR NOT NULL
);

CREATE TABLE IF not exists vkteams.users 
(
    id      SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    vacancy    VARCHAR NOT NULL
    
);

CREATE TABLE IF not exists vkteams.calendar
(
    id      SERIAL PRIMARY KEY,
    VacancyId INTEGER NOT NULL,
    description    VARCHAR  NOT NULL,
    full_description    VARCHAR  NOT NULL,
    filter JSON


   
);