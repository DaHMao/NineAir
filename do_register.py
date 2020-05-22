from AQ.AQ_register import Register
from AQ.setting import *
from AQ.get_phone_v import *
from AQ.save_phone_pwd import r
from apscheduler.schedulers.blocking import BlockingScheduler


def do_do_register():
    pwd = random_password()
    phone = GetNumberCodeByBM(aip_token).do_get_phone_number()
    if isinstance(phone, dict):
        return phone
    user = {
        "user": phone,
        "pwd": pwd
    }
    reg = Register(data=user)
    res_00 = reg.do_register()
    if res_00.get("status") == 0:
        r.save_phone_number(
            phone=phone,
            pwd=pwd
        )
        return "注册成功"
    else:
        return res_00

def do_register_do():
    while r.get_phone_len() <= 15:
        res = do_do_register()
        print(res)
    return True


from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()
# scheduler.add_job(Mail().send_mail, trigger='cron', day=1, hour=1, minute=10)
scheduler.add_job(do_register_do, trigger='cron', hour=9, minute=6)
scheduler.start()
