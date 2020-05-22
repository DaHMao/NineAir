import requests
import urllib3
from AQ.save_cookies import r

urllib3.disable_warnings()


class Backfill(object):
    def __init__(self, data):
        self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Ap" \
                  "pleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
        self.user = data.get("loginInfo").get("loginUser")
        self.pwd = data.get("loginInfo").get("loginPwd")
        self.orderNo = data.get("orderNo")
        self.session = requests.session()
        self.cookie = ""

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
            "Cookie": self.cookie,
        }
        data = {"language": "zh_CN", "currency": "CNY", "password": self.pwd, "loginName": self.user}
        res = self.session.post(url=url, headers=headers, json=data, verify=False)
        if res.status_code == 200:
            for i in self.session.cookies.items():
                if i[1] is None:
                    self.cookie += i[0] + '' + '; '
                else:
                    self.cookie += i[0] + '=' + i[1] + '; '
            r.save_cookie(key=self.user, value=self.cookie)
            return True
        return {
            "status": 3,
            "msg": "登录失败",
        }

    def get_order_details(self):
        """
        获取订单详情
        :return:
        """
        url = f"http://www.9air.com/order/api/order/my-flight-order/{self.orderNo}?language=zh_CN&" \
            f"currency=CNY&channelNo=B2C&passengerName=&credentialsNo="
        headers = {
            "Host": "www.9air.com",
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "Pragma": "no-cache",
            "Cache-Control": "must-revalidate",
            "Accept-Language": "zh_CN",
            "User-Agent": self.ua,
            "Expires": "0",
            "Referer": f"http://www.9air.com/zh-CN/member/ticketorderdetail/{self.orderNo}",
            "Accept-Encoding": "gzip, deflate",
            "Cookie": self.cookie,
        }
        res = self.session.get(url=url, headers=headers, verify=False)
        if res.status_code == 200:
            res_json = res.json()

            pass
        return {
            "status": 3,
            "msg": "登录失败",
        }


    def do_backfill(self):
        pass


if __name__ == "__main__":
    Data = {
        "orderNo": "131231231",
        "loginInfo": {
            "loginType": "",
            "loginUser": "user",
            "loginPwd": "pwd"
        }
    }
    backfill = Backfill(data=Data)
    backfill.do_backfill()
