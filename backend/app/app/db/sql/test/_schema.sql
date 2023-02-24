create type user_role as enum (
    'admin',
    'anon',
    'manager'
);

create table if not exists "user"
(
    id bigserial primary key,
    email text unique not null,
    hashed_password text,
    "role" user_role not null default 'anon',
    full_name text,
    username text unique not null,
    age smallint,
    phone varchar(20),
    avatar text,
    is_active boolean not null default true,
    "is_superuser" boolean not null default false,
    created_at timestamptz default localtimestamp,
    updated_at timestamptz default localtimestamp,
    constraint c_username_is_not_role check ( username != "role"::text),
    constraint c_full_name_is_not_role check ( full_name != "role"::text)
);
