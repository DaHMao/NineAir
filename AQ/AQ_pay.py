# --coding:utf-8--
from lxml import etree
import traceback
from AQ.aq_user import UserOrder
from AQ.setting import *
from AQ.Proxys import *


urllib3.disable_warnings()


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


class Pay(object):
    def __init__(self, data):
        self.ua = random.choice(USER_AGENT)
        self.user = data.get("loginInfo").get("loginUser")
        self.pwd = data.get("loginInfo").get("loginPwd")
        self.orderNo = data.get("orderNo")
        self.totalPrice = data.get("totalPrice")
        self.session = requests.session()
        self.cookie = ""
        self.memberId = ""
        self.pay_list_url = ""
        self.ip = None

    def get_cookies(self):
        res = UserOrder().get_other_user(user=self.user)
        print(res)
        if res.get("data").get("session"):
            if res.get("data").get("ip"):
                self.ip = {
                    'https': f'{res.get("data").get("ip")}:{res.get("data").get("port")}'}
            self.cookie = res.get("data").get("session").split("|")[0]
            self.memberId = res.get("data").get("session").split("|")[1]
        else:
            res["status"] = 404
            res["msg"] = f"请求账号中心获取{self.user}cookies 失败"
            return res

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

    @try_except_request
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
        res = self.session.get(url=url, headers=headers, params=data, verify=False, proxies=self.ip)
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

    @try_except_request
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
        res = self.session.post(url=url, headers=headers, json=data, verify=False, proxies=self.ip)
        if res.status_code == 200:
            self.pay_list_url = res.json().get("data").get("url")
            return True
        return {
            "status": 3,
            "msg": "进入支付方式选项页面失败",
        }

    @try_except_request
    def get_cashier_token(self):
        """
        获取cashier_token 参数
        :return:
        """
        res = requests.get(url=self.pay_list_url, verify=False, proxies=self.ip)
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

    @try_except_request
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
        res = requests.post(url=url, headers=headers, data=data, verify=False, proxies=self.ip)
        if res.status_code == 200:
            res_json = res.json()
            if res_json.get("status") == "success":
                alipay_url = res_json.get("callbackUrl")
                return alipay_url, self.orderNo, self.totalPrice, "AQ", self.user, self.pwd
            else:
                return {
                    "status": 3,
                    "msg": "获取支付链接失败",
                }
        else:
            return {
                "status": 3,
                "msg": "获取支付链接失败",
            }

    def do_pay(self):
        try:
            res_01 = self.get_cookies()
            if isinstance(res_01, dict):
                res_01["index"] = "get_cookies"
                return res_01
            res_02 = self.get_order_pay()
            if isinstance(res_02, dict):
                res_02["index"] = "get_order_pay"
                return res_02
            res_03 = self.post_payment_apply()
            if isinstance(res_03, dict):
                res_03["index"] = "get_order_pay"
                return res_03
            res_04 = self.get_cashier_token()
            if isinstance(res_04, dict):
                res_04["index"] = "get_cashier_token"
                return res_04
            res_05 = self.post_checkout_cashier(cashier_token=res_04)
            return res_05
        except Exception as e:
            print(e)
            return {
                "status": 500,
                "msg": "获取支付链接失败:" + traceback.format_exc(),
            }


if __name__ == "__main__":
    Data = {
        "vcode": "",
        "extra": "",
        "orderNo": "20200701B2COW9022478",
        "totalPrice": 549,
        "flights": {
            "name": "",
            "flightNo": "AQ1168",
            "depDate": "2020-06-12 16:05"
        },
        "loginInfo": {
            "loginType": "",
            "loginUser": "17031311614",
            "loginPwd": "SZgDxg@7867"
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
