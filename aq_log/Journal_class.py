import requests
from datetime import datetime, timezone, timedelta


class Journal(object):
    def __init__(self):
        pass

    @staticmethod
    def get_time():
        """
        获取当前东8区的时间字符串
        :return:
        """
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        now_zone8 = now.astimezone(timezone(timedelta(hours=8)))
        return now_zone8.isoformat()

    def save_journal_register(self, massage="success", level="Info"):
        """
        注册 日志
        :param massage: 返回结果
        :param level:
        :return:
        """
        url = "http://192.168.0.212:8081/log/save"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "project": "九元航空",  # 项目名称
            "module": "注册",  # 模块名称
            "message": massage,  # string 日志内容文本
            "time": self.get_time(),  # string 一定有T，Z
            "level": level,  # 日志等级 info warn error fatal
            "user": "毛大华",  # string 工号， 用于发送钉钉消息
        }
        r = requests.post(url, json=data, headers=headers)
        return r.json()

    def save_journal_search(self, massage="success", level="Info"):
        """
        询价日志
        :param massage:
        :param level:
        :return:
        """
        url = "http://192.168.0.212:8081/log/save"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "project": "九元航空",  # 项目名称
            "module": "询价",  # 模块名称
            "message": massage,  # string 日志内容文本
            "time": self.get_time(),  # string 一定有T，Z
            "level": level,  # 日志等级 info warn error fatal
            "user": "毛大华",  # string 工号， 用于发送钉钉消息
        }
        r = requests.post(url, json=data, headers=headers)
        return r.json()

    def save_journal_order(self, massage="success", level="Info"):
        """
        生单日志
        :param massage:
        :param level:
        :return:
        """
        url = "http://192.168.0.212:8081/log/save"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "project": "九元航空",  # 项目名称
            "module": "生单",  # 模块名称
            "message": massage,  # string 日志内容文本
            "time": self.get_time(),  # string 一定有T，Z
            "level": level,  # 日志等级 info warn error fatal
            "user": "毛大华",  # string 工号， 用于发送钉钉消息
        }
        r = requests.post(url, json=data, headers=headers)
        return r.json()

    def save_journal_pay(self, massage="success", level="Info"):
        """
        支付日志
        :param massage:
        :param level:
        :return:
        """
        url = "http://192.168.0.212:8081/log/save"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "project": "九元航空",  # 项目名称
            "module": "支付",  # 模块名称
            "message": massage,  # string 日志内容文本
            "time": self.get_time(),  # string 一定有T，Z
            "level": level,  # 日志等级 info warn error fatal
            "user": "毛大华",  # string 工号， 用于发送钉钉消息
        }
        r = requests.post(url, json=data, headers=headers)
        return r.json()

    def save_journal_backfill(self, massage="success", level="Info"):
        """
        回填日志
        :param massage:
        :param level:
        :return:
        """
        url = "http://192.168.0.212:8081/log/save"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "project": "九元航空",  # 项目名称
            "module": "票号回填",  # 模块名称
            "message": massage,  # string 日志内容文本
            "time": self.get_time(),  # string 一定有T，Z
            "level": level,  # 日志等级 info warn error fatal
            "user": "毛大华",  # string 工号， 用于发送钉钉消息
        }
        r = requests.post(url, json=data, headers=headers)
        return r.json()


if __name__ == '__main__':
    t = Journal()
