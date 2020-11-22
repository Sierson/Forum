create table users (
    id serial primary key,
    login text not null,
    password text not null
);

create table posts (
    id serial primary key,
    user_id integer not null,
    title text not null,
    content text
);

