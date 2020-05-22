import re
import requests
import time

aip_token = "9a8553c606c2c837187614cd1ce2b926540aebeb"  # 接码平台api


def str_code(s):
    """
    :param s:
    :return:
    """
    re_s = re.findall(r"\d+", s)
    return re_s[0]


def get_token(name):
    url = f"http://to.banma1024.com/api/do.php?action=loginIn&name={name}&password=a12345678@"
    res = requests.get(url=url)
    l_res = res.text.split("|")
    if l_res[0] == "1":
        token = l_res[1]
        return token
    else:
        return {
            "status": 3,
            "msg": f"斑马登录失败，{l_res[1]}",
        }


class GetNumberCodeByBM(object):
    def __init__(self, name):
        self.token = name
        self.sid = "17608"
        self.phone = ""

    def get_phone(self):
        """
        获取注册手机号
        :return:
        """
        url = f"http://to.banma1024.com/api/do.php?action=getPhone&sid={self.sid}&token={self.token}&vno=0 "
        res = requests.get(url=url)
        if res.status_code == 200:
            l_res = res.text.split("|")
            if l_res[0] == "1":
                print(l_res[1][:2])
                if str(l_res[1][:2]) in ("13", "15", "18", "17"):
                    return l_res[1]
                else:
                    self.get_add_black_list(phone=l_res[1])
                    return {
                        "status": 3,
                        "msg": f"重新获取手机号",
                    }
            else:
                return {
                    "status": 3,
                    "msg": f"斑马获取phone失败，{l_res[1]}",
                }
        else:
            return {
                "status": 3,
                "msg": f"斑马获取phone失败",
            }

    def get_message(self, phone):
        """
        获取对应账号的短信验证码
        :return:
        """
        url = f"http://to.banma1024.com/api/do.php?action=getMessage&sid={self.sid}&phone={phone}&token={self.token}"
        res = requests.get(url=url)
        l_res = res.text.split("|")
        if l_res[0] == "1":
            return str_code(s=l_res[1])
        else:
            return {
                "status": 3,
                "msg": f"斑马获取短信失败，{l_res[1]}",
            }

    def get_add_black_list(self, phone):
        """
        将获取的手机号加入黑名单
        :return:
        """
        url = f"http://to.banma1024.com/api/do.php?action=addBlacklist&sid={self.sid}&phone={phone}&token={self.token}"
        res = requests.get(url=url)
        print(res.text)

    def get_cancel_recv(self):
        """
        释放指定账号
        :return:
        """
        url = f"http://to.banma1024.com/api/do.php?action=cancelRecv&" \
            f"sid={self.sid}&phone={self.phone}&token={self.token}"
        res = requests.get(url=url)
        print(res.text)

    def do_get_phone_number(self):
        """
        获取手机号
        :return:
        """
        i = 0
        while i < 10:
            res = self.get_phone()
            if isinstance(res, str):
                return res
            i += 1
        else:
            return {
                "status": 3,
                "msg": "斑马获取phone失败",
            }

    def do_get_phone_message(self, phone):
        """
        获取短信验证码
        :param phone:
        :return:
        """
        i = 0
        while i < 30:
            res = self.get_message(phone=phone)
            if isinstance(res, str):
                return res
            i += 1
            time.sleep(2)
        else:
            self.get_add_black_list(phone=phone)
            return {
                "status": 3,
                "msg": "斑马获取验证码失败",
            }


if __name__ == "__main__":
    pass
