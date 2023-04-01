create or replace function pg_current_wal_insert_lsn_MB() returns text
    language plpgsql as
$$
declare
    pg_current_wal_insert_lsn text;
begin
    select pg_current_wal_insert_lsn() into pg_current_wal_insert_lsn;
    select round(bytes / (8e+6), 0) || 'MB' pg_current_wal_insert_lsn
    from (select ('x' || lpad(split_part(pg_current_wal_insert_lsn, '/', 1), 8, '0'))::bit(32)::bigint << 32 |
                 ('x' || lpad(split_part(pg_current_wal_insert_lsn, '/', 2), 8, '0'))::bit(32)::bigint as bytes) as mb
    into pg_current_wal_insert_lsn;
    return pg_current_wal_insert_lsn;
end;
$$;


create or replace function checkpoint_count() returns text
    language plpgsql as
$$
declare
    checkpoint_count text;
begin
    select total_checkpoints
    from (select (checkpoints_timed + checkpoints_req) as total_checkpoints
          from pg_stat_bgwriter) as sub
    into checkpoint_count;
    return checkpoint_count;
end;
$$;

select checkpoint_count();

select * from pg_stat_bgwriter;