/* source_db/fdw.sql */

create extension if not exists postgres_fdw;

--target_server
drop server if exists target_server cascade;
create server target_server
    foreign data wrapper postgres_fdw
    options (host 'auth_service_postgresql_target_db', port '5432', dbname 'target_db');

--user_mapping
drop user mapping if exists for CURRENT_USER server target_server;
create user mapping for CURRENT_USER
    server target_server
    options (user 'postgres', password 'postgres');

--foreign_table
drop foreign table if exists employee_mapping;
create foreign table employee_mapping (
    id bigserial options (column_name 'f_id') not null ,
    name varchar(255) options (column_name 'f_name') not null ,
    salary integer options (column_name 'f_salary') not null ,
    date date options (column_name 'f_date') not null
    ) server target_server options (table_name 'employee');

select *
from employee limit 3;

select *
from employee_mapping limit 3;