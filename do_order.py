from AQ.AQ_order import Order
from AQ.AQ_login import Login
from AQ.save_phone_pwd import r
from aq_log.Journal_class import Journal
from aq_log.loghelper import __write_log__
import json


def do_order(d, llog=""):
    log = ""
    phone = r.get_a_phone_number()
    data = {
        "user": phone[0],
        "pwd": phone[1],
        "passengers": d.get("passengers")
    }
    print(data)
    login = Login(data=data).do_add_passenger_login()
    if isinstance(login, dict):
        return login
    d.get("loginInfo")["loginUser"] = phone[0]
    d.get("loginInfo")["loginPwd"] = phone[1]
    order = Order(data=d).do_order()
    resp = {
        "请求数据": d,
        "响应数据": order
    }
    if order.get("status") == 500:
        Journal().save_journal_order(massage=json.dumps(resp), level="error")
    else:
        Journal().save_journal_order(massage=json.dumps(resp))
    log = log + str(json.dumps(resp)) + '\n'
    __write_log__(log, tag="_order_")
    return order


if __name__ == "__main__":
    Data = {
        "vcode": "",
        "extra": "",
        "adultNum": 1,
        "childNum": 0,
        "infantNum": 0,
        "priceInfo": {"extra": "PDT2003220954", "proType": "", "cabin": "BR", "adtPrice": 209, "adtTax": 50,
                      "chdPrice": 0,
                      "chdTax": 0,
                      "infPrice": 0, "infTax": 0, "reducePrice": 0, "seats": 18, "rule": ""},
        "flight": {
            "tripType": 1,
            "departure": "CSX",
            "arrival": "HAK",
            "depTime": "2020-05-27 12:45 ",
            "flightNo": "AQ1145"

        },
        "passengers": [
            {
                "name": "李美花",
                "ageType": "ADT",
                "birthday": "1995-10-18",
                "gender": "F",
                "cardType": "ID",
                "cardNum": "46000319951018204X",
                "mobile": ""
            }
        ],
        "contact": {
            "name": "龚俊明",
            "firstName": "",
            "lastName": "",
            "mobile": "15310255777",
            "email": ""
        },
        "loginInfo": {
            "loginType": "",
            "loginUser": "",
            "loginPwd": ""
        }
    }
    do_order(d=Data)
