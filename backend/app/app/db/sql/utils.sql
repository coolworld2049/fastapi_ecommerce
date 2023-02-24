create or replace function truncate_tables_where_owner(username in varchar) returns void as $$
declare
    statements cursor for
        select tablename from pg_tables
        where tableowner = username and schemaname = 'public';
begin
    for stmt in statements loop
        execute 'truncate table ' || quote_ident(stmt.tablename) || ' cascade;';
    end loop;
end;
$$ language plpgsql;
