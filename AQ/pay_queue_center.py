# encoding=utf8
import json
import time
import pika
import uuid
from pika.exceptions import AMQPConnectionError


class MsgRpcClient(object):

    def __init__(self, username: str, password: str, host: str, port: int, virtual_host, heart_beat: int, exchange: str, routing_key: str, queue: str, socket_timeout: int, time_out: int) -> None:
        """
        MsgRpcClient初始化
        :param username: RabbitMQ主机的用户名
        :param password: RabbitMQ主机的密码
        :param host: RabbitMQ主机的IP地址
        :param port: RabbitMQ主机的端口
        :param virtual_host: 服务端绑定的虚拟主机名
        :param heart_beat: 连接后，客户端与RabbitMQ主机保持心跳检测的超时时间
        :param exchange: 服务端绑定的交换机
        :param routing_key: 服务端绑定的routing_key
        :param queue: 服务端监听的队列
        :param socket_timeout: 客户端与RabbitMQ主机连接超时时间
        :param time_out: 客户端与RabbitMQ响应超时时间
        """
        credentials = pika.PlainCredentials(username=username, password=password)  # 创建配置对象
        # 配置MQ主机和心跳,当超过心跳时间未与MQ主机联系,主机就会销毁这个链接,报错“pika.exceptions.StreamLostError”,socket_timeout连接超时限制
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host, port, virtual_host, credentials, heartbeat=heart_beat, socket_timeout=socket_timeout))
        self.channel = self.connection.channel()  # 创建通道
        self.corr_id = str(uuid.uuid1())  # 消息标识
        self.queue = queue  # 服务端所监听的队列
        self.exchange = exchange  # 服务端监听队列绑定的交换机
        self.routing_key = routing_key  # 服务端绑定的routing_key
        self.callback_queue = f'{self.queue}_应答_{self.corr_id}'  # 用于响应的回调队列
        self.channel.queue_declare(queue=self.callback_queue, exclusive=True)  # 设置通道监听的队列(没有则创建),设置排他性为True(只在当前链接中使用,意味着队列中不会有其他消费者,当链接断开后,队列也跟随消失)
        self.channel.basic_consume(queue=self.callback_queue, on_message_callback=self.on_response, auto_ack=False)  # 监听回调队列,添加回调函数,不用ack(链接消失,队列就会消失,消息也会消失)
        self.response = None  # 接收服务端内容的字段
        self.time_out = time_out  # 设置响应超时，单位:s

    def on_response(self, *args):
        props = args[2]
        body = args[3]
        if self.corr_id == props.correlation_id:  # 核验消息标识
            self.response = body

    def call(self, data: str):
        # 向服务端推送消息data(指定exchange,routing_key,reply_to,correlation_id)
        self.channel.basic_publish(exchange=self.exchange, routing_key=self.routing_key, properties=pika.BasicProperties(reply_to=self.callback_queue, correlation_id=self.corr_id), body=data)
        start_time = time.time()
        while self.response is None:
            self.connection.process_data_events(time_limit=0)  # 刷新当前链接中的数据事件,同时与MQ主机保持联系,可以避免heartbeat超时引起报错(阻塞函数,阻塞时间为time_limit),
            end_time = time.time()
            if end_time - start_time > self.time_out:  # 超时检测
                self.connection.close()  # 响应超时后关闭连接,销毁队列,不再接收应答,不关闭的话,待heartbeat超时也会关闭,及时关闭可以减少运行资源占用
                raise TimeoutError
        self.connection.close()  # 正常响应后关闭连接
        return self.response.decode()


if __name__ == '__main__':
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
        'bankUrl': 'https://www.yeepay.com/app-merchant-proxy/node?p0_Cmd=Buy&p1_MerId=10014355533&p2_Order=202005131158510026997973&p3_Amt=450&p4_Cur=CNY&p5_Pid=&p6_Pcat=&p7_Pdesc=&p8_Url=http'
                   '://www.westair.cn/airp-pay/notify/yeepayNotify&p9_SAF=0&pa_MP=%7B%22deviceType%22%3A%22NORMAL%22%2C%22bankCode%22%3A%22YEEPAY%22%2C%22totalFee%22%3A%22450%22%2C%22lang%22%3A'
                   '%22zh_cn%22%7D&pd_FrpId=&pr_NeedResponse=1&hmac=62b00206f200e66835a025d925504486',
        'totalPrice': 459.1,
        'orderNo': '0026997973',
        'airline': 'PN'
    }
    _data = json.dumps(_data, ensure_ascii=False)
    try:
        response = MsgRpcClient(**param).call(_data)
        print(f"pass→收到  {response} ")
    except AMQPConnectionError:
        print("fail→连接失败")
    except TimeoutError:
        print("fail→响应超时")
    except Exception:
        print("fail→支付异常")

