import redis
import random


class RedisClientClass:
    def __init__(self):
        pool = redis.ConnectionPool(host='192.168.1.101', port=6379, decode_responses=True, db=6,
                                    password='')
        self.r = redis.Redis(connection_pool=pool)

    def save_phone_number(self, phone, pwd):
        self.r.lpush(phone, pwd)

    def get_phone_len(self):
        res = self.r.keys()
        return len(res)

    def get_a_phone_number(self):
        try:
            a = random.choice(self.r.keys())
            b = self.r.lpop(name=a)

            return a, b
        except IndexError:
            return {
                "code": 500,
                "msg": "没有可用账号"
            }

    def delete_phone_number(self, phone):
        self.r.delete(phone)


r = RedisClientClass()
# print(r.get_a_phone_number())
# L = [
#     {
#         "user": "18730384165",
#         "pwd": "ASDDFFF1222"
#     },
#     {
#         "user": "13546690604",
#         "pwd": "XvANvQ@1558"
#     },
#     {
#         'user': '17054882066',
#         'pwd': 'WGiBJJ@8031'},
#     {
#         'user': '17031311614',
#         'pwd': 'SZgDxg@7867'}
# ]
# for a in L:
# ('13042881640', 'JmZLxu@6851')
r.save_phone_number(phone="13546690604", pwd="XvANvQ@1558")
