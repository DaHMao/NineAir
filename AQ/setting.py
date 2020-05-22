import random

aip_token = "9a8553c606c2c837187614cd1ce2b926540aebeb"  # 接码平台api

Id_type = {
    "ID": "NI",
    "PP": "PP",
}


def random_password():
    """
    生成随机账号密码
    :return:
    """
    pwd_1 = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    pwd_2 = "0123456789"
    pwd = ''.join(random.choices(pwd_1, k=6)) + "@" + ''.join(random.choices(pwd_2, k=4))
    return pwd


