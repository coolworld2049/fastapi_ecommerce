do
$do$
    begin
        if (select is_role_exists('admin')) then

            raise notice 'role "admin" already exists. skipping.';
        else
            create role admin noinherit createrole;
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


grant usage on all sequences in schema public to admin;
grant all privileges on all tables in schema public to admin;
grant usage, select, update on all sequences in schema public to admin;
