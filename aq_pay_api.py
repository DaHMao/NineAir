# -*- coding: utf-8 -*-

import functools
import json
import threading
import time
import pika
import requests
import datetime
from pika.spec import BasicProperties
from functools import singledispatch
from do_pay import do_do_pay


APP_NAME = "九元航空"
APP_VERSION = "v1.0"
AUTHOR = "MDH"


class PushLog(object):
    def __init__(self, routing_key, headers, connection, channel):
        self.routing_key = routing_key
        self.headers = headers
        self.connection = connection
        self.channel = channel
        self.app_name = APP_NAME
        self.app_version = APP_VERSION
        self.author = AUTHOR

    def send_log(self, msg, is_info, flag):
        data = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "level": "INFO" if is_info else "ERROR",
            "message": flag,
            "properties": {
                "traceProperty": {
                    "traceId": self.headers.get("traceid"),
                    "processId": self.headers.get("processid"),
                    "processStage": get_process_stage(self.routing_key)
                },
                "applicationProperty": {
                    "applicationName": self.app_name,
                    "applicationVersion": self.app_version,
                    "applicationModule": get_process_stage(self.routing_key),
                    "author": self.author
                },
                "dataProperty": msg
            }}
        url = "http://192.168.0.100:5000/api/LogCenter/NewLog"
        r = requests.post(url, json=data)
        try:
            print("code status:", r.status_code)
        except Exception:
            print("存储日志请求失败， 请查实原因！:")


def return_error(content, start_time):
    print("content", content)
    content, msg, flag = content
    error_dic = {1: "身份错误", 2: "非法IP", 3: "操作失败IP",
                 4: "请求参数错误", 5: "程序异常", 9: "访问超时",
                 10: "访问频繁", 11: "无航班数据",
                 36: "代理IP不可用", 101: "请输入验证码"}
    if flag == 0:
        elapsed = int((time.time() - start_time) * 1000)
        print(start_time, time.time(), (time.time() - start_time) * 1000)
        print("flag 0:time", elapsed)
        content['elapsed'] = elapsed
        return json.dumps(content, ensure_ascii=False)

    elif flag == 101:
        jsn = {"status": flag,
               "msg": "请识别并输入验证码",
               "imgBase64": content if isinstance(content, str) else content.decode(),
               "extra": content,
               "taskId": ""}
        return jsn

    else:
        if error_dic.get(flag):
            jsn = {"status": flag,
                   "msg": error_dic.get(flag) + msg}
        else:
            jsn = {"status": flag, "msg": msg}
        return jsn


@singledispatch
def return_info(content, start_time):
    time_ = int((time.time() - start_time) * 1000)
    if isinstance(content, str):
        content = json.loads(content)
    content["elapsed"] = time_
    return content


@return_info.register(tuple)
def _(content, start_time):
    if len(content) == 3:
        return return_error(content, start_time)


@return_info.register(list)
def _(content, start_time):
    print("content is a list:", content)
    content[0]["elapsed"] = int((time.time() - start_time) * 1000)
    return content[0]


def get_process_stage(routing_key):
    if "生单" in routing_key:
        return "生单"
    elif "票号获取" in routing_key:
        return "回填"
    elif "支付" in routing_key:
        return "支付"
    elif "退票查询" in routing_key:
        return "退票查询"
    elif "退票" in routing_key and "查询退票" not in routing_key:
        return "退票"
    else:
        return "询价"


class PIKA(object):
    def __init__(self, *args):
        self.queue_list = list(args)
        self.retry_list = []
        self.extra()
        # 建立连接
        credentials = pika.PlainCredentials('ys', 'ysmq')  # 连接的账号和密码
        parameters = pika.ConnectionParameters('192.168.0.100', credentials=credentials,
                                               heartbeat=5)  # 连接参数 credentials--认证参数
        self.connection = pika.BlockingConnection(parameters)  # 连接 RabbitMQ
        self.channel = self.connection.channel()  # 创建频道
        # 流量控制
        self.channel.basic_qos(prefetch_count=3)
        # 设定消费队列
        self.threads = []
        # 使用到的线程集合
        '''定义一个回调函数on_message_callback，用来接收生产者发送的消息'''
        on_message_callback = functools.partial(self.on_message, args=(self.connection, self.threads))
        [self.channel.basic_consume(queue=name,  # 指定取消息的队列名
                                    on_message_callback=on_message_callback  # 调用回调函数，从队列里取消息
                                    ) for name in self.queue_list]
        # 开始消费数据
        try:
            print('开始消费数据...')
            self.channel.start_consuming()  # 开始循环取消息
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            # 等待所有的线程结束
            for thread in self.threads:
                thread.join()
            # 关闭连接
            self.connection.close()

    def do_work(self, conn, ch, delivery_tag, reply_to, routing_key, body, properties, headers):
        # 开始处理消息
        time.sleep(2)
        ret = self.handle_business(routing_key, body, headers, conn, ch)
        ret = json.dumps(ret)
        # 消息处理完成
        # 将返回数据添加到YS.应答中
        try:
            print(ret)
            if reply_to:
                send_message = functools.partial(self.send_message, ch, "system.response", reply_to, ret,
                                                 properties=properties)
                conn.add_callback_threadsafe(send_message)
            else:
                print('此次操作无须应答')
        except Exception:
            ret = json.dumps({"status": 0})
        # 此任务完成，返回完成信号
        # 有如下内容，ac 掉
        ret_dic = json.loads(ret)
        print(ret_dic.get("status"))
        if ret_dic.get("code") or ret_dic.get("code") in [0, "0"]:
            flag = ret_dic.get("code")
        elif ret_dic.get("status") or ret_dic.get("status") in [0, "0"]:
            flag = ret_dic.get("status")
        else:
            print("返回信息字段不正确")
            flag = "1"
        print("flag:", flag)
        if flag in (0, "0"):
            cb = functools.partial(self.ack_message, ch, delivery_tag, True)
        else:
            cb = functools.partial(self.ack_message, ch, delivery_tag, True)
        conn.add_callback_threadsafe(cb)
        print('----生单时间 ', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), ' [end]----',
              '\n')

    @staticmethod
    def handle_business(routing_key, body, headers, connection, ch):
        start_time = time.time()
        body = json.loads(body.decode())
        print(body)
        ac = do_do_pay(data_r=body, llog=PushLog(routing_key, headers, connection, ch).send_log)
        ret = ac
        info = return_info(ret, start_time)
        return info

    def on_message(self, ch, method_frame, _header_frame, body, args):
        # 四个参数为标准格式 ch, method, properties, body
        (conn, thrds) = args
        delivery_tag = method_frame.delivery_tag
        routing_key = method_frame.routing_key
        reply_to = _header_frame.reply_to
        headers = _header_frame.headers
        properties = BasicProperties(
            correlation_id=_header_frame.correlation_id,
            headers=_header_frame.headers
        )
        t = threading.Thread(target=self.do_work, args=(conn, ch, delivery_tag, reply_to, routing_key, body, properties,
                                                        headers))
        t.start()
        thrds.append(t)

    @staticmethod
    def send_message(ch, exchange_name, route_key, body, properties=None):
        if ch.is_open:
            ch.basic_publish(exchange_name, route_key, body, properties=properties)
        else:
            # 线程处理期间，连接被关闭了，需要妥善处理
            pass

    @staticmethod
    def ack_message(ch, delivery_tag, is_success):
        if ch.is_open:
            if is_success:
                ch.basic_ack(delivery_tag)
            else:
                ch.basic_nack(delivery_tag)
        else:
            # 线程处理期间，连接被关闭了，需要妥善处理
            pass

    @staticmethod
    def extra():
        pass


if __name__ == '__main__':
    PIKA(
        "YS.机票.国内.生单.同程券",
    )
