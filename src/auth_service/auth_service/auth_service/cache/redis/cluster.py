from redis.asyncio.client import Redis

startup_nodes = [{"host": "127.0.0.1", "port": "6379"}, {"host": "127.0.0.1", "port": "7000"}]
redis_cluster = Redis(host='localhost', port=6379)
