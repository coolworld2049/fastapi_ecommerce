/* source_db/init.sql */

-- drop database if exists source_db;
-- create database source_db;

drop table if exists employee;
create table employee
(
    id     bigserial primary key,
    name   varchar(255),
    salary integer,
    date   date
);

--insert_data
drop table if exists ts_series;
create temporary table if not exists ts_series as
select row_number() over () as id, date_trunc('month', dd)::date as dt
from generate_series('2022-10-01'::timestamp,
                     '2023-06-30'::timestamp,
                     '1 month'::interval) as dd;

truncate table employee;
insert into employee(name, salary, date)
    (select random()::text    as name,
            random()::integer as salary,
            dt                as date
     from ts_series);