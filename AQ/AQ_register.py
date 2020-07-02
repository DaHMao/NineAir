# --coding:utf-8--
from AQ.get_phone_v import GetNumberCodeByBM
from AQ.setting import *
from AQ.Proxys import *
from requests.exceptions import ConnectionError, ConnectTimeout, ReadTimeout, ProxyError
from urllib3.exceptions import MaxRetryError, NewConnectionError
from OpenSSL.SSL import Error, WantReadError
import traceback
import json


class Register(object):
    def __init__(self, data):
        self.ua = random.choice(USER_AGENT)
        self.user = data.get("user")
        self.pwd = data.get("pwd")
        proxy = get_proxy()
        self.ip = proxy[0]
        self.host = proxy[1]
        print(proxy)

    def get_verification_code(self):
        """
        获取短信验证码
        :return:
        """
        url = "http://www.9air.com/member/api/member/verification-code/send?language=zh_CN&currency=CNY"
        headers = {
            "Host": "www.9air.com",
            "Connection": "keep-alive",
            "Content-Length": "99",
            "Pragma": "no-cache",
            "Accept-Language": "zh_CN",
            "User-Agent": self.ua,
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "Cache-Control": "must-revalidate",
            "Expires": "0",
            "Origin": "http://www.9air.com",
            "Referer": "http://www.9air.com/zh-CN/regist",
            "Accept-Encoding": "gzip, deflate",
        }
        data = {"language": "zh_CN", "currency": "CNY", "event": 1, "type": "SMS", "phoneCode": "CN",
                "phone": self.user}
        res = requests.post(url=url, headers=headers, json=data, verify=False, proxies=self.ip)
        if res.status_code == 200:
            print("发送验证码成功")
            return True
        else:
            return {
                "status": 3,
                "msg": f"注册失败，发送验证码失败,{res.json().get('msg')}"
            }

    def post_register(self, verification_code):
        """
           提交注册
        :param verification_code:
        :return:
        """
        url = "http://www.9air.com/member/api/member/b2c/account/register?language=zh_CN&currency=CNY"
        headers = {
            "Host": "www.9air.com",
            "Connection": "keep-alive",
            "Content-Length": "190",
            "Pragma": "no-cache",
            "Accept-Language": "zh_CN",
            "User-Agent": self.ua,
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "Cache-Control": "must-revalidate",
            "Expires": "0",
            "Origin": "http://www.9air.com",
            "Referer": "http://www.9air.com/zh-CN/regist",
            "Accept-Encoding": "gzip, deflate",
        }
        data = {"language": "zh_CN", "currency": "CNY", "channelNo": "B2C", "type": "SMS", "phoneCode": "CN",
                "phone": self.user, "password": self.pwd, "confirmPassword": self.pwd,
                "verificationCode": verification_code}
        res = requests.post(url=url, headers=headers, json=data, verify=False, proxies=self.ip)
        if res.status_code == 200:
            return {
                "status": 0,
                "msg": "注册成功",
                "phone": self.user,
                "pwd": self.pwd
            }
        return {
            "status": 3,
            "msg": f"注册失败，{res.json().get('msg')}"
        }

    def do_register(self):
        i = 0
        while i < 3:
            try:
                res_01 = self.get_verification_code()
                if res_01:
                    code = GetNumberCodeByBM(aip_token).do_get_phone_message(phone=self.user)
                    if isinstance(code, dict):
                        code["index"] = "do_get_phone_message"
                        return code
                    print("验证码：", code)
                    res_02 = self.post_register(verification_code=code)
                    return res_02
            except (
                    ConnectionError, ConnectTimeout, ReadTimeout, ProxyError, Error, WantReadError, MaxRetryError,
                    NewConnectionError, json.decoder.JSONDecodeError):
                freed_proxy(host=self.host)
                i += 1
            except Exception:
                return {'status': 500, 'msg': traceback.format_exc()}
        else:
            return {
                "status": 3,
                "msg": "注册失败，ip问题，请稍后重试"
            }


if __name__ == "__main__":
    Data = {
        "user": "15128329218",
        "pwd": "yushang2020"
    }
    reg = Register(data=Data)
    reg.do_register()
