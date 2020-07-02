from AQ.AQ_order import Order, get_cookie
from aq_log.Journal_class import Journal
import json
import traceback
import time


def do_order(params, llog=""):
    """
    执行生单
    :param params:
    :return:
    """
    start_time = time.time()
    res_user = get_cookie()
    if isinstance(res_user, dict):
        res_user["status"] = 404
        res_user["index"] = "get_cookie,请求账号中心失败"
        end_time = time.time()
        resp = {
            "请求数据": params,
            "响应数据": res_user,
            "生单耗时": str(end_time - start_time)
        }
        Journal().save_journal_order(massage=json.dumps(resp), level="error", field1=str(end_time - start_time))
        return res_user
    params["loginInfo"]["loginUser"] = res_user[0]
    params["loginInfo"]["loginPwd"] = res_user[1]
    params["ip"] = res_user[2]
    params["cookies"] = res_user[3]
    try:
        order_o = Order(data=params).do_order()
        end_time = time.time()
        resp = {
            "请求数据": params,
            "响应数据": order_o,
            "生单耗时": str(end_time - start_time)
        }
        if order_o.get("status") == 0:
            Journal().save_journal_order(massage=json.dumps(resp), field1=str(end_time - start_time))
        else:
            Journal().save_journal_order(massage=json.dumps(resp), level="warn", field1=str(end_time - start_time))
        return order_o
    except Exception as e:
        print(e)
        ret = {'status': 5, 'msg': traceback.format_exc()}
        end_time = time.time()
        resp = {
            "请求数据": params,
            "响应数据": ret,
            "生单耗时": str(end_time - start_time)
        }
        Journal().save_journal_order(massage=json.dumps(resp), level="error", field1=str(end_time - start_time))
        return ret


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
