from AQ.AQ_login import Login
import time

Data = {
    "airline": "AQ",
    "user": "13042881640",
    "password": "JmZLxu@6851",
    "ip": "",
    "port": "",
    "session": "SESSION=19204797-d2d2-40a8-a6e3-24949a86e301; token=F3296D4FC22E4967AF2CBD0AC27B29F2"
}

start = time.time()
while True:
    login = Login(data=Data).do_keep_session()
    print(login)
    if login.get("state") == 0:
        time.sleep(90)
    else:
        break
end_time = time.time()
print(end_time-start)

