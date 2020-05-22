from AQ.AQ_pay import Pay
import json
from pika.exceptions import AMQPConnectionError
from AQ.pay_queue_center import MsgRpcClient
from aq_log.Journal_class import Journal
import traceback
from aq_log.loghelper import __write_log__


def do_do_pay(data_r, llog=""):
    log = ""
    pay = Pay(data=data_r).do_pay()
    if isinstance(pay, dict):
        if pay.get("status") == 500:
            resp = {
                "请求数据": data_r,
                "响应数据": pay
            }
            Journal().save_journal_pay(massage=json.dumps(resp), level="error")
            log = log + str(json.dumps(resp)) + '\n'
            __write_log__(log, tag="_pay_")
            return pay
        else:
            resp = {
                "请求数据": data_r,
                "响应数据": pay
            }
            Journal().save_journal_pay(massage=json.dumps(resp))
            log = log + str(json.dumps(resp)) + '\n'
            __write_log__(log, tag="_pay_")
            return pay
    print("开始发送请求...", end="")
    param = {
        "username": "ys",
        "password": "ysmq",
        "host": "192.168.0.100",
        "port": 5672,
        "virtual_host": "/",
        "heart_beat": 6,
        "exchange": "YS.机票.支付",
        "routing_key": "YS.机票.支付.支付中心.支付宝",
        "queue": "YS.机票.支付.支付中心.支付宝",
        "socket_timeout": 10,
        "time_out": 120
    }
    _data = {
        'bankUrl': pay[0],
        'totalPrice': int(pay[1]),
        'orderNo': pay[2],
        'airline': pay[3]
    }
    _data = json.dumps(_data, ensure_ascii=False)
    try:
        response = MsgRpcClient(**param).call(_data)
        print(f"pass→收到  {response} ")
        res = json.loads(response)
        print(type(res))
        if res.get("status") == 0:
            res["payPrice"] = pay[1]
            resp = {
                "请求数据": data_r,
                "响应数据": res
            }
            Journal().save_journal_pay(massage=json.dumps(resp))
            log = log + str(json.dumps(resp)) + '\n'
            __write_log__(log, tag="_pay_")
            return res
        else:
            res["user"] = pay[4]
            res["pwd"] = pay[5]
            resp = {
                "请求数据": data_r,
                "响应数据": res
            }
            Journal().save_journal_pay(massage=json.dumps(resp))
            log = log + str(json.dumps(resp)) + '\n'
            __write_log__(log, tag="_pay_")
            return res
    except AMQPConnectionError:
        print("fail→连接失败")
        pay = {
            "status": 1,
            "msg": f"支付时遇到链接失败，请人工手动登录查看是否支付成功,账号：{pay[4]}，密码：{pay[5]}",
        }
        resp = {
            "请求数据": data_r,
            "响应数据": pay
        }
        Journal().save_journal_pay(massage=json.dumps(resp), level="warn")
        log = log + str(json.dumps(resp)) + '\n'
        __write_log__(log, tag="_pay_")
        return pay
    except TimeoutError:
        pay = {
            "status": 1,
            "msg": f"支付时遇到请求超时，请人工手动登录查看是否支付成功,账号：{pay[4]}，密码：{pay[5]}",
        }
        resp = {
            "请求数据": data_r,
            "响应数据": pay
        }
        Journal().save_journal_pay(massage=json.dumps(resp), level="warn")
        log = log + str(json.dumps(resp)) + '\n'
        __write_log__(log, tag="_pay_")
        return pay
    except Exception:
        pay = {
            "status": 1,
            "msg": f"支付时遇到异常，请人工手动登录查看是否支付成功,账号：{pay[4]}，密码：{pay[5]},"
                   + traceback.format_exc(),
        }
        resp = {
            "请求数据": data_r,
            "响应数据": pay
        }
        Journal().save_journal_pay(massage=json.dumps(resp), level="warn")
        log = log + str(json.dumps(resp)) + '\n'
        __write_log__(log, tag="_pay_")
        return pay
