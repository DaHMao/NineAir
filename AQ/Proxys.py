import random
import requests
from requests.exceptions import ConnectionError, ProxyError, ReadTimeout, ConnectTimeout
import urllib3

urllib3.disable_warnings()


def get_proxy(stop=0):
    global res
    try:
        url = 'http://ip.ystrip.cn:8080/api/Vps/GetUsed?group={}&user=AQ'.format(random.choice(['isearch']))
        res = requests.get(url, timeout=5, verify=False).json()
        if res['ret'] == 1:
            proxy = 'YsProxy:YsProxy@0023' + '@' + str(res['data']['ip']) + ':1808'
            proxies = {'http': 'http://' + proxy, 'https': 'https://' + proxy}
            return proxies, res['data']['host']
        else:
            stop += 1
            if stop > 3:
                return None, None
            return get_proxy(stop=stop)
    except (ConnectionError, ProxyError, ReadTimeout, ConnectTimeout):
        stop += 1
        if stop > 3:
            return None, None
        return get_proxy(stop=stop)


def freed_proxy(host, typ='false'):
    try:
        response = requests.get(
            'http://ip.ystrip.cn:8080/api/Vps/UsedReset?host={}&isDial={}&user=AQ'.format(
                host, typ), timeout=5)
    except (ConnectionError, ProxyError, ReadTimeout, ConnectTimeout):
        return None


if __name__ == '__main__':
    print(freed_proxy(host=""))
    pass
