import requests
import urllib3
from lxml import etree
import traceback

urllib3.disable_warnings()


class Pay(object):
    def __init__(self, data):
        self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Ap" \
                  "pleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
        self.user = data.get("loginInfo").get("loginUser")
        self.pwd = data.get("loginInfo").get("loginPwd")
        self.orderNo = data.get("orderNo")
        self.totalPrice = data.get("totalPrice")
        self.session = requests.session()
        self.cookie = ""
        self.memberId = ""
        self.pay_list_url = ""

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
            self.memberId = res.json().get("data").get("memberId")
            return True
        return {
            "status": 3,
            "msg": "登录失败",
        }

    def get_order_pay(self):
        """
        获取待支付的订单
        :return:
        """
        url = "http://www.9air.com/order/api/order/my-order?"
        data = {
            "language": "zh_CN",
            "currency": "CNY",
            "channelNo": "B2C",
            "orderStatus": "1,7,9",
            "orderType": "",
            "startDate": "",
            "endDate": "",
            "currentPage": "1",
            "pageSize": "5",
            "orderNo": "",
        }
        headers = {
            "Host": "www.9air.com",
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "Pragma": "no-cache",
            "Cache-Control": "must-revalidate",
            "Accept-Language": "zh_CN",
            "User-Agent": self.ua,
            "Expires": "0",
            "Referer": "http://www.9air.com/zh-CN/member/order",
            "Accept-Encoding": "gzip, deflate",
            "Cookie": self.cookie,
        }
        res = self.session.get(url=url, headers=headers, params=data, verify=False)
        if res.status_code == 200:
            res_json = res.json()
            l_order = res_json.get("data").get("data")
            if l_order:
                for order in l_order:
                    if order.get("orderNo") == self.orderNo and int(self.totalPrice) == int(order.get("actualPrice")):
                        return True
                    continue
                else:
                    return {
                        "status": 3,
                        "msg": "匹配订单号和总价失败",
                    }
            else:
                return {
                    "status": 3,
                    "msg": "获取未支付订单列表为空",
                }

        return {
            "status": 3,
            "msg": "获取未支付订单列表详情失败",
        }

    def post_payment_apply(self):
        url = "http://www.9air.com/pay/api/payment/apply?language=zh_CN&currency=CNY"
        headers = {
            "Host": "www.9air.com",
            "Connection": "keep-alive",
            "Content-Length": "231",
            "Pragma": "no-cache",
            "Accept-Language": "zh_CN",
            "User-Agent": self.ua,
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "Cache-Control": "must-revalidate",
            "Expires": "0",
            "Origin": "http://www.9air.com",
            "Referer": "http://www.9air.com/zh-CN/member/order",
            "Accept-Encoding": "gzip, deflate",
        }
        data = {"language": "zh_CN", "currency": "CNY", "amount": self.totalPrice, "channelNo": "B2C", "form": 1,
                "orderNo": self.orderNo, "type": 1, "payer": self.memberId,
                "webCallbackUrl": f"http://www.9air.com/zh-CN/result?orderNumber={self.orderNo}&type=pay"}
        res = self.session.post(url=url, headers=headers, json=data, verify=False)
        if res.status_code == 200:
            self.pay_list_url = res.json().get("data").get("url")
            return True
        return {
            "status": 3,
            "msg": "进入支付方式选项失败",
        }

    def get_cashier_token(self):
        """
        获取cashier_token 参数
        :return:
        """
        res = requests.get(url=self.pay_list_url, verify=False)
        if res.status_code == 200:
            try:
                html = etree.HTML(res.text)
                cashier_token = html.xpath('//input[@id="token"]/@value')[0]
                return cashier_token
            except IndexError:
                return {
                    "status": 3,
                    "msg": "未找cashier_token,该订单已过期",
                }
        else:
            return {
                "status": 3,
                "msg": "获取cashier_token失败",
            }

    def post_checkout_cashier(self, cashier_token):
        """
        获取支付宝支付链接
        :return:
        """
        url = "https://airpay.yeepay.com/ap-cashier-app/cashier/checkout"
        headers = {
            "Host": "airpay.yeepay.com",
            "Connection": "keep-alive",
            "Content-Length": "131",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Sec-Fetch-Dest": "empty",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": self.ua,
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://airpay.yeepay.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Referer": self.pay_list_url,
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        data = {
            "payTool": "ALIPAYAPP",
            "bindCardId": "",
            "bankCode": "",
            "bankName": "",
            "cardLast": "",
            "cashierToken": cashier_token,
            "locale": "zh_CN",
            "cardType": ""
        }
        res = requests.post(url=url, headers=headers, data=data, verify=False)
        if res.status_code == 200:
            res_json = res.json()
            if res_json.get("status") == 200:
                alipay_url = res_json.get("data").get("url")
                return alipay_url, self.orderNo, self.totalPrice, "AQ", self.user, self.pwd
        else:
            return {
                "status": 3,
                "msg": "获取支付链接失败",
            }

    def do_pay(self):
        try:
            res_01 = self.post_login()
            if isinstance(res_01, dict):
                return res_01
            res_02 = self.get_order_pay()
            if isinstance(res_02, dict):
                return res_02
            res_03 = self.post_payment_apply()
            if isinstance(res_03, dict):
                return res_03
            res_04 = self.get_cashier_token()
            if isinstance(res_04, dict):
                return res_04
            res_05 = self.post_checkout_cashier(cashier_token=res_04)
            return res_05
        except Exception:
            return {
                "status": 500,
                "msg": "获取支付链接失败:" + traceback.format_exc(),
            }


if __name__ == "__main__":
    Data = {
        "vcode": "",
        "extra": "",
        "orderNo": "20200521B2COW1697025",
        "totalPrice": 519,
        "flights": {
            "name": "",
            "flightNo": "AQ1055",
            "depDate": "2020-06-12 16:05"
        },
        "loginInfo": {
            "loginType": "",
            "loginUser": "13042881640",
            "loginPwd": "JmZLxu@6851"
        },
        "payment": {
            "payChannel": "",
            "payWay": "Cash",
            "payUser": "",
            "payPwd": ""
        }
    }
    pay = Pay(data=Data)
    print(pay.do_pay())
