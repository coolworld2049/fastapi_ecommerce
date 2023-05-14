### connection limit 
connection limit < max(num_cores, parallel_io_limit) / (session_busy_ratio * avg_parallelism)
- num_cores   
  - количество доступных ядер
  - parallel_io_limit
    - количество одновременных запросов ввода/вывода, которое может обработать ваша подсистема хранения
  - session_busy_ratio
    - это доля времени, в течение которого соединение активно, выполняя оператор в базе данных
  - avg_parallelism
    - среднее количество серверных процессов, работающих над одним запросом.
      - max_parallel_workers и max_parallel_workers_per_gather. 
      - Если max_parallel_workers_per_gather равно 0, средний параллелизм должен быть равен 1
```sql
SELECT datname,
       active_time /
       (active_time + idle_in_transaction_time) AS session_busy_ratio
FROM pg_stat_database
WHERE active_time > 0;
```
