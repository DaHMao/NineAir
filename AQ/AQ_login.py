# --coding:utf-8--
import requests
from AQ.save_cookies import r
from AQ.setting import *
from AQ.Proxys import get_proxy, freed_proxy
import random


def try_except_request(func):
    def fun_1(self, *args, **kwargs):
        try:
            msg = func(self, *args, **kwargs)
            return msg
        except exceptions:
            freed_proxy(host=self.host)
            ip = get_proxy()[0]
            host = get_proxy()[1]
            if ip:
                self.ip = ip
                self.host = host
            else:
                self.ip = None
                self.host = ""
            return eval('self.{}(*args, **kwargs)'.format(func.__name__))

    return fun_1


class Login(object):
    def __init__(self, data):
        self.ua = random.choice(USER_AGENT)
        self.user = data.get("user")
        self.pwd = data.get("password")
        self.session = requests.session()
        if data.get("ip"):
            ip = {
                'https': f'{data.get("ip")}:{data.get("port")}'}
            self.ip = ip
        else:
            self.ip = None
        self.cookie = data.get("session").split("|")[0]
        self.host = ""

    @try_except_request
    def post_login(self):
        """
        登录
        :return:
        """
        url = "http://www.9air.com/member/api/member/b2c/account/login?language=zh_CN&currency=CNY"
        headers = {
            "Host": "www.9air.com",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Accept-Language": "zh_CN",
            "User-Agent": self.ua,
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "Cache-Control": "must-revalidate",
            "Expires": "0",
            "Origin": "http://www.9air.com",
            "Accept-Encoding": "gzip, deflate",
        }
        data = {"language": "zh_CN", "currency": "CNY", "password": self.pwd, "loginName": self.user}
        res = self.session.post(url=url, headers=headers, json=data, verify=False, proxies=self.ip)
        res_json = res.json()
        print(res_json)
        if res_json.get("msg") == "成功" and res_json.get("status") == 200:
            member_id = res.json().get("data").get("memberId")
            cookie = ''
            for i in self.session.cookies.items():
                if i[1] is None:
                    cookie += i[0] + '' + '; '
                else:
                    cookie += i[0] + '=' + i[1] + '; '
            r.save_cookie(key=self.user, value=cookie)
            return {
                "state": 0,
                "msg": "登录成功",
                "session": cookie + "|" + member_id
            }
        else:
            return {
                "state": 1,
                "msg": f"登录失败,{res_json.get('msg')}",
            }

    def post_add_passenger(self, passenger):
        """
        添加乘客
        :return:
        """
        url = "http://www.9air.com/member/api/authenticate/b2c/confirmAuth?language=zh_CN&currency=CNY"
        headers = {
            "Host": "www.9air.com",
            "Connection": "keep-alive",
            "Content-Length": "122",
            "Pragma": "no-cache",
            "Origin": "http://www.9air.com",
            "Accept-Language": "zh_CN",
            "User-Agent": self.ua,
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "Cache-Control": "must-revalidate",
            "Expires": "0",
            "Accept-Encoding": "gzip, deflate",
        }
        data = {"language": "zh_CN", "currency": "CNY", "channelNo": "B2C", "realName": passenger.get("name"),
                "idType": -1,
                "idNumber": passenger.get("cardNum")}
        res = self.session.post(url=url, headers=headers, json=data, verify=False)
        print(res.text)
        if res.status_code == 200:
            print(res.text)
            return True
        return {
            "status": 3,
            "msg": "绑定乘客失败",
        }

    @try_except_request
    def post_growth_grade(self):
        """
        保持cookie有效
        :return:
        """
        url = "http://www.9air.com/member/api/growth/b2c/getGrowthGrade?language=zh_CN&currency=CNY"
        headers = {
            "Host": "www.9air.com",
            "Connection": "keep-alive",
            "Content-Length": "37",
            "Pragma": "no-cache",
            "Accept-Language": "zh_CN",
            "User-Agent": self.ua,
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "Cache-Control": "must-revalidate",
            "Expires": "0",
            "Origin": "http://www.9air.com",
            "Referer": "http://www.9air.com/zh-CN/member",
            "Accept-Encoding": "gzip, deflate",
            "Cookie": self.cookie,
        }
        data = {"language": "zh_CN", "currency": "CNY"}
        res = self.session.post(url=url, headers=headers, json=data, verify=False, proxies=self.ip)
        res_json = res.json()
        print(res_json)
        if res_json.get("msg") == "成功" and res_json.get("status") == 200:
            return {
                "state": 0,
                "msg": "账号在线"
            }
        else:
            return {
                "state": 1,
                "msg": f"账号掉线",
            }

    def do_login(self):
        res_01 = self.post_login()
        return res_01

    def do_keep_session(self):
        res_01 = self.post_growth_grade()
        return res_01


if __name__ == "__main__":
    Data = {
        "airline": "AQ",
        'user': '17031311614',
        'password': 'SZgDxg@7867',
        "ip": "",
        "port": "",
        "session": "SESSION=f1868397-a908-4c9e-8753-b1f1aa3c11fa; token=647D504AD62047089A9CD06238095E62; |5156429 "
    }

    login = Login(data=Data)
    print(login.do_keep_session())

L = {'status': 200, 'code': None, 'msg': '成功',
     'data': {'sessionId': None, 'token': '647D504AD62047089A9CD06238095E62', 'memberId': '5156429',
              'memberBaseInfo': {'name': None, 'nickName': None, 'birthday': None, 'gender': None,
                                 'cellphone': '17031311614', 'email': None, 'headImageUrl': '',
                                 'memberNo': '33126656342', 'nameEn': '', 'cellphoneCode': '86', 'nationality': None,
                                 'regArea': None, 'regTime': '2020-05-20 15:08:20',
                                 'lastLoginTime': '2020-07-01 18:06:49', 'realNameState': '0', 'isNewRegister': '0',
                                 'hasPwd': '1', 'age': None, 'status': '0', 'modPwd': '0', 'registerTerminal': '00',
                                 'registerIp': '113.204.5.6'}, 'memberCertificateList': [], 'walletStatus': 'F',
              'bindValue': None, 'thirdType': None, 'nickName': None, 'headUrl': None}}
