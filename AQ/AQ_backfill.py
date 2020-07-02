# --coding:utf-8--
from AQ.aq_user import UserOrder
from AQ.setting import *
from AQ.Proxys import *
from aq_log.Journal_class import Journal
import traceback
import random

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


class Backfill(object):
    def __init__(self, data):
        self.ua = random.choice(USER_AGENT)
        self.user = data.get("loginInfo").get("loginUser")
        self.pwd = data.get("loginInfo").get("loginPwd")
        self.orderNo = data.get("orderNo")
        self.session = requests.session()
        self.cookie = ""
        self.ip = None

    def get_cookies(self):
        res = UserOrder().get_other_user(user=self.user)
        print(res)
        if res.get("data").get("session"):
            if res.get("data").get("ip"):
                self.ip = {
                    'https': f'{res.get("data").get("ip")}:{res.get("data").get("port")}'}
            self.cookie = res.get("data").get("session").split("|")[0]
            # self.memberId = res.get("data").get("session").split("|")[1]
        else:
            res["status"] = 404
            res["msg"] = f"请求账号中心获取---{self.user}------cookies 失败"
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
            if res_json.get("status") == 200:
                data_datail = res_json.get("data")
                if data_datail.get("status") in ("5", "6") and data_datail.get("orderNo") == self.orderNo:
                    ticket_nos = []
                    passengers = data_datail.get("passengers")
                    for passenger in passengers:
                        if passenger.get("ticketStatus") in ("2",):
                            ticket_nos.append({
                                "name": passenger.get("fullName"),
                                "ticketNo": passenger.get("ticketNo"),
                                "fare": float(passenger.get("actualPrice")),
                                "segType": "",
                            })
                    pay_infos = []
                    payments = data_datail.get("payments")
                    for payment in payments:
                        if payment.get("status") in ("3", 3):
                            pay_infos.append({
                                "payStatus": "已支付",
                                "currency": payment.get("currency"),
                                "payPrice": payment.get("amount"),
                                "payTradeNo": payment.get("paymentSerialNo"),
                                "payChannel": "Alipay",
                                "payWay": "Cash",
                                "payTime": payment.get("completionTime")
                            })
                    backfill_order = {
                        "status": 0,
                        "msg": "success",
                        "orderNo": self.orderNo,
                        "orderStatus": "已支付",
                        "ticketNos": ticket_nos,
                        "payInfos": pay_infos
                    }
                    return backfill_order
                else:
                    # 3 表示 已取消
                    # 6 表示 交易完成
                    return {
                        "status": 3,
                        "msg": f"暂未获取到票号，请稍后重试，订单状态为---{data_datail.get('status')}---"
                    }
            else:
                return {
                    "status": 3,
                    "msg": f"回填失败，{res_json.get('msg')}",
                }
        else:
            return {
                "status": 5,
                "msg": f"回填请求未成功,该账号未获取到对应的订单，响应数据为：{res.text}",
            }

    def do_backfill(self):
        res_01 = self.get_cookies()
        if res_01:
            return res_01
        res_02 = self.get_order_details()
        return res_02

    def do_backfill_text(self):
        self.post_login()
        return self.get_order_details()


def do_do_backfill(params):
    if params.get("orderNo") and params.get("loginInfo").get("loginUser"):
        try:
            backfill = Backfill(data=params).do_backfill()
            resp = {
                "请求数据": params,
                "响应数据": backfill
            }
            if resp.get("status") in (0,3):
                Journal().save_journal_backfill(massage=json.dumps(resp))
            else:
                Journal().save_journal_backfill(massage=json.dumps(resp), level="warn")
            return backfill
        except Exception as e:
            print(e)
            ret = {
                "status": 500,
                "msg": f"请求异常，{traceback.format_exc()}"
            }
            resp = {
                "请求数据": params,
                "响应数据": ret
            }
            Journal().save_journal_backfill(massage=json.dumps(resp), level="error")
            return ret
    else:
        ret = {
            "status": 4,
            "msg": "请求缺少必要参数"
        }
        resp = {
            "请求数据": params,
            "响应数据": ret
        }
        Journal().save_journal_backfill(massage=json.dumps(resp), level="error")
        return ret


if __name__ == "__main__":
    Data = {
        "orderNo": "20200701B2COW1787238",
        "loginInfo": {
            "loginType": "",
            "loginUser": "15922908607",
            "loginPwd": "LuoDan19920727"
        }
    }
    backfill_ = Backfill(data=Data)
    print(backfill_.do_backfill_text())
