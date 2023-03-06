do
$do$
    begin
        if (select is_role_exists('admin')) then
            raise notice 'role "admin" already exists. skipping.';
        else
            create role admin noinherit createrole nobypassrls;
        end if;
    end
$do$;

do
$do$
    begin
        if (select is_role_exists('user')) then
            raise notice 'role "user" already exists. skipping.';
        else
            create role "user" noinherit;
        end if;
    end
$do$;

grant execute on all routines in schema public to admin;
grant execute on all routines in schema public to "user";

alter table "user"
    enable row level security;


grant usage on all sequences in schema public to admin;
grant all privileges on all tables in schema public to admin;
grant usage, select, update on all sequences in schema public to admin;


/*
drop policy if exists admin_can_crud_all on "user";
create policy admin_can_crud_all on "user" for all to admin
    using (username = session_user);

*/


grant usage on all sequences in schema public to "user";
grant select, update, insert on "user" to "user";


/*
drop policy if exists user_can_cru_self on "user";
create policy user_can_cru_self on "user" as permissive for all to "user"
    using (username = session_user);

drop policy if exists user_cant_d_self on "user";
create policy user_cant_d_self on "user" as restrictive for delete to "user"
    using (username = session_user);

drop policy if exists user_can_r_all on "user";
create policy user_can_r_all on "user" as permissive for select to "user"
    using ("role" = 'admin'::user_role);

*/
