s = """
Host: www.9air.com
Connection: keep-alive
Accept: application/json, text/plain, */*
Pragma: no-cache
Cache-Control: must-revalidate
Accept-Language: zh_CN
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36
Expires: 0
Referer: http://www.9air.com/zh-CN/member/ticketorderdetail/20200521B2COW2045145
Accept-Encoding: gzip, deflate


"""
dd = {}
for a in s.split("\n"):
    b = '"' + a.replace(': ', '": "') + '",'
    print(b)
