create or replace function is_role_exists(name text)
    returns setof boolean as
$$
begin
    return query select exists(
                                select
                                from pg_catalog.pg_roles
                                where rolname = name);
end
$$ language plpgsql;




create or replace function get_role_by_username(_username text)
    returns setof text as
$$
begin
    return query select role from "user" where username = _username;
end
$$ language plpgsql;


create or replace function create_user_in_role(db_user text, password text, current_user_role text, db_name text)
    returns void as
$$
declare
    query text := 'create user ';
begin
    if db_user is not null and password is not null and current_user_role is not null then
        query := query || db_user || ' inherit login password ' || quote_nullable(password) || ' in role ' ||
                 current_user_role;
    end if;
    execute query;
    execute format('grant connect on database %s to %s;', db_name, db_user);
end
$$ language plpgsql;



create or replace function change_user_password(username text, old_password text, new_password text) returns void
as
$$
begin
    execute 'alter user ' || username || ' identified by ' || old_password || ' replace ' || new_password;
end;
$$ language plpgsql;


/*
-- Функция для создания пользователей
create procedure create_role(name text, surname text,
                            login text, password text,
                            mobile_number bigint, email text,
                            code smallint)
as $$
declare
    granted_role text;
begin
    if (select count(*) from pg_roles where rolname=login) then
        raise exception 'such user already exists';
    else
        execute format('create role %i with login password %l;',
                        login, password);
        granted_role := (select position_name
            from user_role_classifier
            where position_code = code);
        execute format('grant %i to %i;', granted_role, login);
        execute format('grant connect on database clients_database to %i;',
                       granted_role, login);
        commit;
    end if;
end; $$
language plpgsql;


create function delete_employee_role() returns trigger
as $$
begin
    execute format('drop role %i;', old.employee_login);
    return null;
end; $$
language plpgsql;


create trigger role_delete_trigger
after delete on employees
for each row
execute function delete_employee_role();
*/
