
--group role by username
with recursive cte as (
   select oid from pg_roles where rolname = 'admin'

   union all
   select m.roleid
   from   cte
   join   pg_auth_members m on m.member = cte.oid
   )
select oid, oid::regrole::text as rolename from cte;  -- oid & name
