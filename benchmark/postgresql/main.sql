drop table if exists test_users;
create table if not exists test_users
(
    id            serial,
    customer_name varchar(255),
    total_amount  numeric,
    created_at    timestamp
);

do
$$
    declare
        rnd integer;
        max integer = 10000;
    begin
        for i in 1..max
            loop
                rnd = floor(random() * max * 100 + 1)::integer;
                insert into test_users(customer_name, total_amount, created_at)
                values (rnd::varchar(255), i::numeric, localtimestamp);

                update test_users
                set total_amount = total_amount - 1
                where id = floor(random() * (select count(*) from test_users));

                delete from test_users where id = floor(random() * (select count(*) from test_users));
            end loop;
    end;
$$ language plpgsql;

select pg_current_wal_insert_lsn_MB();
