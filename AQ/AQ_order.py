# --coding:utf-8--
from AQ.save_cookies import r
from AQ.setting import *
from AQ.Proxys import *
import datetime
from requests.exceptions import ConnectionError, ConnectTimeout, ReadTimeout, ProxyError
from urllib3.exceptions import MaxRetryError, NewConnectionError
from OpenSSL.SSL import Error, WantReadError
import traceback
import json



class Order(object):
    def __init__(self, data):
        self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Ap" \
                  "pleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
        self.session = requests.session()
        self.user = data.get("loginInfo").get("loginUser")
        self.pwd = data.get("loginInfo").get("loginPwd")
        self.cookies = r.get_cookie(key=self.user)
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
        proxy = get_proxy()
        self.ip = proxy[0]
        self.host = proxy[1]
        print(proxy)

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
                    "msg": "生单失败，匹配产品名失败"
                }
        else:
            return {
                "status": 3,
                "msg": "生单失败，查询航班失败," + res.json().get("msg")

            }

    def analysis_flight(self, flights):
        """
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

    def post_shop_order_no(self):
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
        data = {"language": "zh_CN", "currency": "CNY", "sessionId": self.sessionId,
                "channelNo": "B2C", "tripType": self.tripType, "contactName": self.contact_name, "contactEmail": "",
                "contactPhone": self.contact_mobile, "phoneCountry": "CN",
                "price": int(self.total_price) - int(self.couponPrice),
                "deductions": [
                    {"targetType": "SEGMENT", "targetNumber": 0, "type": "2", "amount": int(self.couponPrice),
                     "content": self.couponId,
                     "credentialsNo": self.passengers[0].get("cardNum"),
                     "credentialsType": Id_type[self.passengers[0].get("cardType")], "flightId": self.flightID}],
                "passengerInfos": [
                    {"isBeneficiary": "true", "firstNameEN": "", "lastNameEN": "",
                     "nameCN": self.passengers[0].get("name"), "idtype": Id_type[self.passengers[0].get("cardType")],
                     "idcard": self.passengers[0].get("cardNum"), "certificateNation": "CN", "validDate": "",
                     "nation": "CN",
                     "gender": self.passengers[0].get("gender"), "birthDate": self.Birthday,
                     "contactPhoneCountry": "CN",
                     "contactPhone": self.contact_mobile,
                     "spIdType": "", "_switch": "CN", "baby": self.infantNum, "child": self.childNum, "guardianID": "",
                     "guardianName": "",
                     "id": 0,
                     "type": self.passengers[0].get("ageType"), "_useName": self.passengers[0].get("name"),
                     "save": True, "nationality": "CN",
                     "credentialsInfos": [
                         {"credentialsNo": self.passengers[0].get("cardNum"),
                          "type": Id_type[self.passengers[0].get("cardType")],
                          "credentialsNationality": "CN",
                          "validDate": ""}],
                     "passengerSegmentInfos": [
                         {"flightID": self.flightID, "cabinClass": self.bookClass, "subClass": self.cabin,
                          "productNo": self.code,
                          "passengerAncillaryServices": [], "id": 0}]}]}
        res = self.session.post(url=url, headers=headers, json=data, verify=False, proxies=self.ip)
        print(res.json())
        if res.status_code == 200:
            res_ok = res.json()
            return {
                "status": 0,
                "msg": "success",
                "currency": "CNY",
                "totalPrice": int(self.total_price) - int(self.couponPrice),
                "orderNo": res_ok.get("data").get("orderNo"),
                "pnr": res_ok.get("data").get("pnr"),
                "loginUser": self.user,
                "loginPwd": self.pwd,
            }
        else:
            return {
                "status": 3,
                "msg": "生单失败，校验是否有红包可以使用失败"
            }

    def do_order(self):
        i = 0
        while i < 3:
            try:
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
                res_04 = self.post_coupon_check()
                if isinstance(res_04, dict):
                    res_04["index"] = "post_coupon_check"
                    return res_04
                res_05 = self.post_coupon()
                if isinstance(res_05, dict):
                    res_05["index"] = "post_coupon_check"
                    return res_05
                res_06 = self.post_shop_order_no()
                return res_06
            except (
                    ConnectionError, ConnectTimeout, ReadTimeout, ProxyError, Error, WantReadError, MaxRetryError,
                    NewConnectionError, json.decoder.JSONDecodeError):
                i += 1
                freed_proxy(host=self.host)
            except Exception:
                return {'status': 500, 'msg': traceback.format_exc()}
        else:
            return {
                "status": 3,
                "msg": "询价失败，ip问题，请稍后重试"
            }


if __name__ == "__main__":
    Data = {
        "vcode": "",
        "extra": "",
        "adultNum": 1,
        "childNum": 0,
        "infantNum": 0,
        "priceInfo": {"extra": "PDT2003220954", "proType": "", "cabin": "BR", "adtPrice": 209, "adtTax": 50,
                      "chdPrice": 0,
                      "chdTax": 0,
                      "infPrice": 0, "infTax": 0, "reducePrice": 0, "seats": 18, "rule": ""},
        "flight": {
            "tripType": 1,
            "departure": "CSX",
            "arrival": "HAK",
            "depTime": "2020-05-27 12:45 ",
            "flightNo": "AQ1145"

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
            "mobile": "15310255777",
            "email": ""
        },
        "loginInfo": {
            "loginType": "",
            "loginUser": "18206848096",
            "loginPwd": "uxKbFr@5823"
        }
    }
    order = Order(data=Data)
    print(order.do_order())
