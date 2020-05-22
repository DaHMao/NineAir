import redis


class RedisClientClass:
    def __init__(self):
        pool = redis.ConnectionPool(host='192.168.1.101', port=6379, decode_responses=True, db=7,
                                    password='')
        self.r = redis.Redis(connection_pool=pool)

    def save_cookie(self, value, key, name="AQ"):
        self.r.hset(name=name, key=key, value=value)

    def get_cookie(self, key, name="AQ"):
        return self.r.hget(name=name, key=key)


r = RedisClientClass()

