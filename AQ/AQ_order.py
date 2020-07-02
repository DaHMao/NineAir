# --coding:utf-8--
from AQ.setting import *
from AQ.Proxys import *
from AQ.aq_user import UserOrder
import datetime
from aq_log.loghelper import __write_log__
import random


def try_except_request(func):
    def fun_1(self, *args, **kwargs):
        try:
            msg = func(self, *args, **kwargs)
            return msg
        except exceptions:
            freed_proxy(host=self.host)
            ip = get_proxy()[0]
            host = get_proxy()[1]
            if ip:
                self.ip = ip
                self.host = host
            else:
                self.ip = None
                self.host = ""
            return eval('self.{}(*args, **kwargs)'.format(func.__name__))

    return fun_1


def get_cookie():
    """
    从账号中心获取账号
    :return:
    """
    res_user = UserOrder().get_user()
    print("或者账号是否成功：", res_user)
    if res_user.get("state") == 0:
        user = res_user["data"]["user"]
        pwd = res_user["data"]["password"]
        ip = {
            'https': f'{res_user.get("data").get("ip")}:{res_user.get("data").get("port")}'}
        cookies = res_user.get("data").get("session").split("|")[0]
        return user, pwd, ip, cookies
    else:
        return res_user


class Order(object):
    def __init__(self, data):
        self.ua = random.choice(USER_AGENT)
        self.session = requests.session()
        self.user = data.get("loginInfo").get("loginUser")
        self.pwd = data.get("loginInfo").get("loginPwd")
        self.cookies = data.get("cookies")
        self.tripType = "OW" if data.get("flight").get("tripType") == 1 else "MT"
        self.adultNum = data.get("adultNum")
        self.childNum = data.get("childNum")
        self.infantNum = data.get("infantNum")
        self.departure = data.get("flight").get("departure")
        self.arrival = data.get("flight").get("arrival")
        self.flightNo = data.get("flight").get("flightNo")
        self.depTime = data.get("flight").get("depTime")[:10]
        self.passengers = data.get("passengers")
        self.code = data.get("priceInfo").get("extra")
        self.price = data.get("priceInfo").get("adtPrice")
        self.tax = data.get("priceInfo").get("adtTax")
        self.total_price = self.price + self.tax
        self.cabin = data.get("priceInfo").get("cabin")
        self.Birthday = self.passengers[0].get("birthday")
        self.birthday = (datetime.datetime.strptime(self.Birthday, '%Y-%m-%d') - datetime.timedelta(days=1)).strftime(
            '%Y-%m-%d')
        self.contact_name = data.get("contact").get("name")
        self.contact_mobile = data.get("contact").get("mobile")
        self.product_name = ""
        self.bookClass = ""
        self.arriveDate = ""
        self.arrivalTime = ""
        self.departDate = ""
        self.departTime = ""
        self.planeType = ""
        self.flightID = ""
        self.couponPrice = ""
        self.couponId = ""
        self.sessionId = ""
        self.passenger_list = []
        self.ip = data.get("ip", None)

    def get_passenger_list(self):
        """
        [{"idNo":"513436200005199192","idType":"NI","name":"李柯"}]
        :return:
        """
        for passenger in self.passengers:
            id_type = Id_type[passenger.get("cardType")]
            if id_type:
                self.passenger_list.append(
                    {"idNo": passenger.get("cardNum"),
                     "idType": id_type,
                     "name": passenger.get("name")}
                )
            else:
                return {
                    "status": 3,
                    "msg": f"生单失败，还不支持{passenger.get('cardType')}证件类型生单，请联系开发人员添加此功能"
                }

    @try_except_request
    def search_flight(self):
        """
        搜索航班
        :return:
        """
        url = "http://www.9air.com/shop/api/shopping/b2c/searchflight?"
        headers = {
            "Host": "www.9air.com",
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "Pragma": "no-cache",
            "Cache-Control": "must-revalidate",
            "Accept-Language": "zh_CN",
            "User-Agent": self.ua,
            "Expires": "0",
            "Accept-Encoding": "gzip, deflate",
            "Cookie": self.cookies,
        }
        data = {
            "language": "zh_CN",
            "currency": "CNY",
            "flightCondition": f"index:0;depCode:{self.departure};arrCode:{self.arrival};depDate:{self.depTime};"
            f"depCodeType:CITY;arrCodeType:AIRPORT;",
            "channelNo": "B2C",
            "tripType": self.tripType,
            "groupIndicator": "I",
            "adultCount": self.adultNum,
            "childCount": self.childNum,
            "infantCount": self.infantNum,
            "airlineCode": "",
            "directType": "",
            "cabinClass": "",
            "taxFee": "",
            "taxCurrency": "",
            "promotionCode": ""
        }
        res = self.session.get(url=url, headers=headers, params=data, verify=False, proxies=self.ip)
        if res.status_code == 200:
            res_flight = self.analysis_flight(flights=res.json())
            if isinstance(res_flight, dict):
                res_flight["index_01"] = "analysis_flight"
                return res_flight
            self.sessionId = res.json().get("data").get("sessionId")
            products = res.json().get("data").get("products")
            for product in products:
                if product.get("code") == self.code:
                    self.product_name = product.get("name")
                    return True
            else:
                return {
                    "status": 3,
                    "msg": "生单失败，匹配产品失败"
                }
        else:
            return {
                "status": 3,
                "msg": "生单失败，查询航班失败," + res.json().get("msg")

            }

    def analysis_flight(self, flights):
        """
        解析航程信息
        :return:
        """
        flight_l = flights.get("data").get("flights")
        if flight_l:
            for flight01 in flight_l:
                for flight in flight01:
                    fares = flight.get("fares")
                    if fares:
                        for fare in fares:
                            if fare.get("productNo") == self.code:
                                if int(self.total_price) == fare.get("price") and self.cabin == fare.get("subClass"):
                                    self.bookClass = fare.get("cabinClass")
                                    segment = flight.get("segments")[0]
                                    self.arriveDate = segment.get("arrivalDate")
                                    self.arrivalTime = segment.get("arrivalTime")
                                    self.departDate = segment.get("departDate")
                                    self.departTime = segment.get("departTime")
                                    self.planeType = segment.get("planeType")
                                    self.flightID = flight.get("flightId")
                                    return True
            else:
                return {
                    "status": 3,
                    "msg": "生单失败，校验价格和舱位失败"
                }
        else:
            return {
                "status": 3,
                "msg": "生单失败，该航段无所查询的航班"
            }

    @try_except_request
    def get_checkin_seat(self):
        """
        校验舱位
        :return:
        """
        url = "http://www.9air.com/modAndRef/api/checkin/seat?"
        headers = {
            "Host": "www.9air.com",
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "Pragma": "no-cache",
            "Cache-Control": "must-revalidate",
            "Accept-Language": "zh_CN",
            "User-Agent": self.ua,
            "Expires": "0",
            "Accept-Encoding": "gzip, deflate",
            "Cookie": self.cookies,
        }
        data = {
            "language": "zh_CN",
            "currency": "CNY",
            "oOperFltNo": self.flightNo[2:],
            "oFltOrgDate": self.depTime,
            "oOperAirlineCode": self.flightNo[:2],
            "flag": "0",
            "destApt": self.arrival,
            "deptApt": self.departure,
        }
        res = self.session.get(url=url, headers=headers, params=data, verify=False, proxies=self.ip)
        if res.status_code == 200:
            return True
        else:
            return {
                "status": 3,
                "msg": "生单失败，校验舱位失败," + res.json().get("msg")
            }

    @try_except_request
    def check_passenger_information(self):
        """
        添加乘机人并校验乘机人信息
        :return:
        """
        url = "http://www.9air.com/member/api/beneficiary/b2c/account/" \
              "checkBeneficicaryByList?language=zh_CN&currency=CNY"
        headers = {
            "Host": "www.9air.com",
            "Connection": "keep-alive",
            "Content-Length": "107",
            "Pragma": "no-cache",
            "Accept-Language": "zh_CN",
            "User-Agent": self.ua,
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "Cache-Control": "must-revalidate",
            "Expires": "0",
            "Origin": "http://www.9air.com",
            "Accept-Encoding": "gzip, deflate",
            "Cookie": self.cookies,
        }
        data = {"language": "zh_CN", "currency": "CNY",
                "lists": self.passenger_list}
        res = self.session.post(url=url, headers=headers, json=data, verify=False, proxies=self.ip)
        if res.status_code == 200:
            return True
        else:
            return {
                "status": 3,
                "msg": "生单失败，添加乘机人并校验乘机人信息失败," + res.json().get("msg")
            }

    def post_coupon_check(self):
        """
        校验是否有红包可以使用
        :return:
        """
        url = "http://www.9air.com/member/api/coupon/b2c/checkCanUse?language=zh_CN&currency=CNY"
        headers = {
            "Host": "www.9air.com",
            "Connection": "keep-alive",
            "Content-Length": "1014",
            "Pragma": "no-cache",
            "Accept-Language": "zh_CN",
            "User-Agent": self.ua,
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "Cache-Control": "must-revalidate",
            "Expires": "0",
            "Origin": "http://www.9air.com",
            "Referer": "http://www.9air.com/zh-CN/book/confirm",
            "Accept-Encoding": "gzip, deflate",
            "Cookie": self.cookies,
        }
        data = {"language": "zh_CN", "currency": "CNY", "accountType": "", "amount": self.total_price, "subPoints": "0",
                "channelNo": "B2C", "isRefundOrder": "", "orderStatus": "", "orderType": "",
                "passengers": [
                    {"actualPrice": self.price, "birthday": self.birthday,
                     "credentialsNo": self.passengers[0].get("cardNum"),
                     "credentialsType": Id_type[self.passengers[0].get("cardType")], "fare": self.price,
                     "gender": self.passengers[0].get("gender"), "issuanceDate": "", "mprInfo": "",
                     "passengerName": self.passengers[0].get("name"),
                     "passengerType": self.passengers[0].get("ageType"), "paxMemberType": "", "_peopleId": 0,
                     "segList": [
                         {"tax": "", "type": "D", "PriceType": "", "actualPrice": int(self.price),
                          "_actualPrice": int(self.total_price),
                          "amount": int(self.price),
                          "arriveDate": self.arriveDate, "arriveTime": self.arrivalTime, "bookClass": self.bookClass,
                          "carrier": self.flightNo[:2],
                          "couponCouponId": "", "departDate": self.departDate, "departTime": self.departTime,
                          "destCode": self.arrival,
                          "discount": "10", "fightNo": self.flightNo[2:], "id": "", "itemServiceList": [], "name": "",
                          "orgCode": self.departure,
                          "passengerId": 0, "planeType": self.planeType, "segIndex": 1,
                          "serviceType": self.product_name,
                          "travelDirect": ""}],
                     "specialType": "", "ticketStatus": ""}], "refundType": "", "routeType": self.tripType,
                "travelItinerary": [{"mailAddress": "", "rightsId": "", "rightsTime": ""}], "type": ""}
        res = self.session.post(url=url, headers=headers, json=data, verify=False, proxies=self.ip)
        # print(res.text)
        if res.status_code == 200:
            self.couponId = res.json().get("data").get("data").get("bestCodes")[0]
            self.couponPrice = res.json().get("data").get("data").get("order").get("couponPrice")
            return True
        else:
            return {
                "status": 3,
                "msg": "生单失败，校验是否有红包可以使用失败," + res.json().get("msg")
            }

    def post_coupon(self):
        """
        校验是否有红包可以使用
        :return:
        """
        url = "http://www.9air.com/member/api/coupon/b2c/calculateDiscount?language=zh_CN&currency=CNY"
        headers = {
            "Host": "www.9air.com",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Accept-Language": "zh_CN",
            "User-Agent": self.ua,
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "Cache-Control": "must-revalidate",
            "Expires": "0",
            "Origin": "http://www.9air.com",
            "Referer": "http://www.9air.com/zh-CN/book/confirm",
            "Accept-Encoding": "gzip, deflate",
            "Cookie": self.cookies,
        }
        data = {"language": "zh_CN", "currency": "CNY", "accountType": "", "amount": int(self.total_price),
                "subPoints": "0", "channelNo": "B2C", "isRefundOrder": "", "orderStatus": "", "orderType": "",
                "passengers": [
                    {"actualPrice": int(self.price), "birthday": f"{self.birthday}T16:00:00.000Z",
                     "credentialsNo": self.passengers[0].get("cardNum"),
                     "credentialsType": Id_type[self.passengers[0].get("cardType")], "fare": int(self.price),
                     "gender": self.passengers[0].get("gender"),
                     "issuanceDate": "", "mprInfo": "",
                     "passengerName": self.passengers[0].get("name"),
                     "passengerType": self.passengers[0].get("ageType"),
                     "paxMemberType": "", "_peopleId": 0,
                     "segList": [
                         {"tax": "", "type": "D", "PriceType": "", "actualPrice": int(self.price),
                          "_actualPrice": int(self.total_price),
                          "amount": int(self.price),
                          "arriveDate": self.arriveDate, "arriveTime": self.arrivalTime, "bookClass": self.bookClass,
                          "carrier": self.flightNo[:2],
                          "couponCouponId": "", "departDate": self.departDate, "departTime": self.departTime,
                          "destCode": self.arrival,
                          "discount": "10", "fightNo": self.flightNo[2:], "id": "", "itemServiceList": [], "name": "",
                          "orgCode": self.departure,
                          "passengerId": 0, "planeType": self.planeType, "segIndex": 1,
                          "serviceType": self.product_name,
                          "travelDirect": ""}],
                     "specialType": "", "ticketStatus": ""}],
                "refundType": "", "routeType": self.tripType,
                "travelItinerary": [{"mailAddress": "", "rightsId": "", "rightsTime": ""}], "type": ""}
        res = self.session.post(url=url, headers=headers, json=data, verify=False, proxies=self.ip)
        # print(res.text)
        if res.status_code == 200:
            amount = res.json().get("data").get("data").get("amount")
            print(amount)
            if int(amount) == int(self.total_price):
                return True
            else:
                return {
                    "status": 3,
                    "msg": "生单失败，价格校验失败"
                }
        else:
            return {
                "status": 3,
                "msg": "生单失败，校验是否有红包可以使用失败," + res.json().get("msg")
            }

    def get_passenger_infos(self):
        passenger_infos_l = []
        i_d = 0
        i_d_t = 0
        for passenger in self.passengers:
            if passenger.get("ageType") == "ADT":
                id_type = Id_type[passenger.get("cardType")]
                passenger_infos_l.append(
                    {
                        "isBeneficiary": "false", "firstNameEN": "", "lastNameEN": "",
                        "nameCN": passenger.get("name"), "idtype": id_type,
                        "idcard": passenger.get("cardNum"), "certificateNation": "CN", "validDate": "", "nation": "CN",
                        "gender": passenger.get("gender"),
                        "birthDate": passenger.get("birthday"), "contactPhoneCountry": "CN",
                        "contactPhone": passenger.get("mobile"),
                        "spIdType": "",
                        "_switch": "CN", "baby": 0, "child": 0,
                        "guardianID": "",
                        "guardianName": "", "id": i_d,
                        "type": "ADT",
                        "_useName": passenger.get("name"), "save": True, "nationality": "CN",
                        "credentialsInfos": [
                            {"credentialsNo": passenger.get("cardNum"), "type": id_type, "credentialsNationality": "",
                             "validDate": ""}],
                        "passengerSegmentInfos": [
                            {"flightID": self.flightID, "cabinClass": self.bookClass, "subClass": self.cabin,
                             "productNo": self.code,
                             "passengerAncillaryServices": [], "id": i_d_t}]})
                i_d += 1
                i_d_t += 100
            else:
                continue
        passenger_infos_l[0]["baby"] = self.infantNum
        passenger_infos_l[0]["child"] = self.childNum
        for passenger in self.passengers:
            if passenger.get("ageType") == "INF":
                id_type = Id_type[passenger.get("cardType")]
                passenger_infos_l.append(
                    {
                        "isBeneficiary": "false", "firstNameEN": "", "lastNameEN": "",
                        "nameCN": passenger.get("name"), "idtype": id_type,
                        "idcard": passenger.get("cardNum"), "certificateNation": "CN", "validDate": "", "nation": "CN",
                        "gender": passenger.get("gender"),
                        "birthDate": passenger.get("birthday"), "contactPhoneCountry": "CN",
                        "contactPhone": passenger.get("mobile"),
                        "spIdType": "",
                        "_switch": "CN", "baby": 0, "child": 0,
                        "guardianID": passenger_infos_l[0].get("id"),
                        "guardianName": passenger_infos_l[0].get("nameCN"), "id": i_d,
                        "type": "INF",
                        "_useName": passenger.get("name"), "save": True, "nationality": "CN",
                        "credentialsInfos": [
                            {"credentialsNo": passenger.get("cardNum"), "type": id_type, "credentialsNationality": "",
                             "validDate": ""}],
                        "passengerSegmentInfos": [
                            {"flightID": self.flightID, "cabinClass": self.bookClass, "subClass": self.cabin,
                             "productNo": self.code,
                             "passengerAncillaryServices": [], "id": i_d_t}]})
                i_d += 1
                i_d_t += 100
            elif passenger.get("ageType") == "CHD":
                id_type = Id_type[passenger.get("cardType")]
                passenger_infos_l.append(
                    {
                        "isBeneficiary": "false", "firstNameEN": "", "lastNameEN": "",
                        "nameCN": passenger.get("name"), "idtype": id_type,
                        "idcard": passenger.get("cardNum"), "certificateNation": "CN", "validDate": "",
                        "nation": "CN",
                        "gender": passenger.get("gender"),
                        "birthDate": passenger.get("birthday"), "contactPhoneCountry": "CN",
                        "contactPhone": passenger.get("mobile"),
                        "spIdType": "",
                        "_switch": "CN", "baby": 0, "child": 0,
                        "guardianID": passenger_infos_l[0].get("id"),
                        "guardianName": passenger_infos_l[0].get("nameCN"), "id": i_d,
                        "type": "CHD",
                        "_useName": passenger.get("name"), "save": True, "nationality": "CN",
                        "credentialsInfos": [
                            {"credentialsNo": passenger.get("cardNum"), "type": id_type,
                             "credentialsNationality": "",
                             "validDate": ""}],
                        "passengerSegmentInfos": [
                            {"flightID": self.flightID, "cabinClass": self.bookClass, "subClass": self.cabin,
                             "productNo": self.code,
                             "passengerAncillaryServices": [], "id": i_d_t}]})
                i_d += 1
                i_d_t += 100
        return passenger_infos_l

    @try_except_request
    def post_shop_order_no(self, passenger_infos):
        """
        生单请求
        :return:
        """
        url = "http://www.9air.com/shop/api/reserve/reserve?language=zh_CN&currency=CNY"
        headers = {
            "Host": "www.9air.com",
            "Connection": "keep-alive",
            "Content-Length": "1130",
            "Pragma": "no-cache",
            "Accept-Language": "zh_CN",
            "User-Agent": self.cookies,
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "Cache-Control": "must-revalidate",
            "Expires": "0",
            "Origin": "http://www.9air.com",
            "Referer": "http://www.9air.com/zh-CN/book/confirm",
            "Accept-Encoding": "gzip, deflate",
            "Cookie": self.cookies,
        }
        data = {
            "language": "zh_CN",
            "currency": "CNY",
            "sessionId": self.sessionId,
            "channelNo": "B2C",
            "tripType": self.tripType,
            "contactName": self.contact_name,
            "contactEmail": "",
            "contactPhone": self.contact_mobile,
            "phoneCountry": "CN",
            "price": int(self.total_price),
            "deductions": [
                # {"targetType": "SEGMENT", "targetNumber": 0, "type": "2", "amount": int(self.couponPrice),
                #  "content": self.couponId,
                #  "credentialsNo": self.passengers[0].get("cardNum"),
                #  "credentialsType": Id_type[self.passengers[0].get("cardType")], "flightId": self.flightID}
            ],
            "passengerInfos": passenger_infos}
        res = self.session.post(url=url, headers=headers, json=data, verify=False, proxies=self.ip)
        print(res.json())
        if res.status_code == 200:
            res_ok = res.json()
            if res_ok.get("status") == 200:
                return {
                    "status": 0,
                    "msg": "success",
                    "currency": "CNY",
                    "totalPrice": int(self.total_price),
                    "orderNo": res_ok.get("data").get("orderNo"),
                    "pnr": res_ok.get("data").get("pnr"),
                    "loginUser": self.user,
                    "loginPwd": self.pwd,
                }
            else:
                log = ""
                log = log + str(json.dumps(res_ok)) + '\n'
                __write_log__(log, tag="_order_")
                return {
                    "status": 3,
                    "msg": f"生单失败,{res_ok.get('msg')}"
                }
        else:
            log = ""
            log = log + str(json.dumps(res.text)) + '\n'
            __write_log__(log, tag="_order_")
            return {
                "status": 3,
                "msg": "生单失败"
            }

    def do_order(self):
        res_00 = self.search_flight()
        if isinstance(res_00, dict):
            res_00["index"] = "search_flight"
            return res_00
        res_01 = self.get_passenger_list()
        if isinstance(res_01, dict):
            res_01["index"] = "get_passenger_list"
            return res_01
        res_02 = self.get_checkin_seat()
        if isinstance(res_02, dict):
            res_02["index"] = "get_checkin_seat"
            return res_02
        res_03 = self.check_passenger_information()
        if isinstance(res_03, dict):
            res_03["index"] = "check_passenger_information"
            return res_03
        res_p = self.get_passenger_infos()
        # -------------------------------------------- 校验和匹配红包 --------------------------------------------------
        # res_04 = self.post_coupon_check()
        # if isinstance(res_04, dict):
        #     res_04["index"] = "post_coupon_check"
        #     return res_04
        # res_05 = self.post_coupon()
        # if isinstance(res_05, dict):
        #     res_05["index"] = "post_coupon_check"
        #     return res_05
        # --------------------------------------------------------------------------------------------------------------
        res_06 = self.post_shop_order_no(passenger_infos=res_p)
        return res_06


def do_order_text(params):
    """
    执行生单
    :param params:
    :return:
    """
    # res_user = get_cookie()
    # if isinstance(res_user, dict):
    #     res_user["status"] = 404
    #     res_user["index"] = "get_cookie,请求账号中心失败"
    #     return res_user
    res_user = ('17031311614', 'SZgDxg@7867', "",
                "SESSION=c04161a9-d929-442f-aed2-8874d61bcf7a; token=647D504AD62047089A9CD06238095E62;")

    params["loginInfo"]["loginUser"] = res_user[0]
    params["loginInfo"]["loginPwd"] = res_user[1]
    params["ip"] = res_user[2]
    params["cookies"] = res_user[3]
    order_o = Order(data=params).do_order()
    return order_o


if __name__ == "__main__":
    Data = {
        "vcode": "",
        "extra": "",
        "adultNum": 1,
        "childNum": 0,
        "infantNum": 0,
        "priceInfo": {'extra': 'PDT2006240989', 'proType': '', 'cabin': 'AP', 'adtPrice': 499, 'adtTax': 50,
                      'chdPrice': 0, 'chdTax': 0,
                      'infPrice': 0, 'infTax': 0, 'reducePrice': 0, 'seats': 6, 'rule': ''},
        "flight": {
            "tripType": 1,
            "departure": "CSX",
            "arrival": "HAK",
            "depTime": "2020-07-27 12:45",
            "flightNo": "AQ1168"
        },
        "passengers": [
            {
                "name": "李美花",
                "ageType": "ADT",
                "birthday": "1995-10-18",
                "gender": "F",
                "cardType": "ID",
                "cardNum": "46000319951018204X",
                "mobile": ""
            }
        ],
        "contact": {
            "name": "龚俊明",
            "firstName": "",
            "lastName": "",
            "mobile": "15310255757",
            "email": ""
        },
        "loginInfo": {
            "loginType": "",
            "loginUser": "",
            "loginPwd": ""
        }
    }
    print(do_order_text(params=Data))
