import requests
from AQ.setting import URL


class UserOrder(object):
    def __init__(self):
        pass

    @staticmethod
    def get_user():
        url = f"{URL}/getFreeUser.do"
        data = {
            "airline": "AQ"
        }
        headers = {
            "Content-Type": "application/json"
        }
        res = requests.post(url=url, json=data, headers=headers).json()
        return res

    @staticmethod
    def delete_user(user):
        url = f"{URL}/setFreeUser.do"
        data = {
            "airline": "AQ",
            "user": user
        }
        headers = {
            "Content-Type": "application/json"
        }
        res = requests.post(url=url, json=data, headers=headers).json()
        return res

    @staticmethod
    def get_other_user(user):
        url = f"{URL}/getUser.do"
        data = {
            "airline": "AQ",
            "user": user
        }
        headers = {
            "Content-Type": "application/json"
        }
        res = requests.post(url=url, json=data, headers=headers).json()
        return res


if __name__ == "__main__":
    # user = "15730519403"
    pass
    # us = User_order()
    # print(us.get_user())
    # print(us.delete_user(user=user))
    # print(us.get_other_user(user))
