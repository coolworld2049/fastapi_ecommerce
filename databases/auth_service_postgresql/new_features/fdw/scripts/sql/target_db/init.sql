/* target_db/init.sql */

-- drop database if exists target_db;
-- create database target_db;

drop table if exists employee;
create table employee
(
    f_id     bigserial primary key,
    f_name   varchar(255),
    f_salary integer,
    f_date   date
);

--insert_data
drop table if exists ts_series;
create temporary table if not exists ts_series as
select row_number() over () as id, date_trunc('month', dd)::date as dt
from generate_series('2020-10-01'::timestamp,
                     '2021-06-30'::timestamp,
                     '1 month'::interval) as dd;

truncate table employee;
insert into employee(f_name, f_salary, f_date)
    (select random()::text    as name,
            random()::integer as salary,
            dt                as date
     from ts_series);