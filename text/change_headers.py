s = """
Host: www.9air.com
Connection: keep-alive
Content-Length: 37
Pragma: no-cache
Accept-Language: zh_CN
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36
Content-Type: application/json;charset=UTF-8
Accept: application/json, text/plain, */*
Cache-Control: must-revalidate
Expires: 0
Origin: http://www.9air.com
Referer: http://www.9air.com/zh-CN/member
Accept-Encoding: gzip, deflate

"""
dd = {}
for a in s.split("\n"):
    b = '"' + a.replace(': ', '": "') + '",'
    print(b)
