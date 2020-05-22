import requests
from AQ.save_cookies import r


class Login(object):
    def __init__(self, data):
        self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Ap" \
                  "pleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
        self.user = data.get("user")
        self.pwd = data.get("pwd")
        self.session = requests.session()
        self.passenger = data.get("passengers")[0]

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
        res = self.session.post(url=url, headers=headers, json=data, verify=False)
        if res.status_code == 200:
            print(res.text)
            cookie = ''
            for i in self.session.cookies.items():
                if i[1] is None:
                    cookie += i[0] + '' + '; '
                else:
                    cookie += i[0] + '=' + i[1] + '; '
            r.save_cookie(key=self.user, value=cookie)
            return True
        return {
            "status": 3,
            "msg": "登录失败",
        }

    def post_add_passenger(self):
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
        data = {"language": "zh_CN", "currency": "CNY", "channelNo": "B2C", "realName": self.passenger.get("name"),
                "idType": -1,
                "idNumber": self.passenger.get("cardNum")}
        res = self.session.post(url=url, headers=headers, json=data, verify=False)
        print(res.text)
        if res.status_code == 200:
            print(res.text)
            return True
        return {
            "status": 3,
            "msg": "绑定乘客失败",
        }

    def do_add_passenger_login(self):
        res_01 = self.post_login()
        if res_01:
            res_02 = self.post_add_passenger()
            return res_02
        return res_01


if __name__ == "__main__":
    Data = {'user': '18206848096', 'pwd': 'uxKbFr@5823', 'passengers': [
        {'name': '文柯', 'ageType': 'ADT', 'birthday': '1989-06-07', 'gender': 'M', 'cardType': 'ID',
         'cardNum': '210102198906079899', 'mobile': ''}]}

    login = Login(data=Data)
    login.post_login()
