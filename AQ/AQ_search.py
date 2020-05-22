# --coding:utf-8--
from AQ.Proxys import *
from requests.exceptions import ConnectionError, ConnectTimeout, ReadTimeout, ProxyError
from urllib3.exceptions import MaxRetryError, NewConnectionError
from OpenSSL.SSL import Error, WantReadError
import traceback
import json



class Search(object):
    def __init__(self, data):
        self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Ap" \
                  "pleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
        self.tripType = "OW" if data.get("tripType") == 1 else "MT"
        self.fromCity = data.get("fromCity")
        self.toCity = data.get("toCity")
        self.fromDate = data.get("fromDate")
        self.adultNum = data.get("adultNum")
        self.childNum = data.get("childNum")
        self.infantNum = data.get("infantNum")
        self.price_L = []
        self.flights_L = []
        self.journeys = []
        proxy = get_proxy()
        self.ip = proxy[0]
        self.host = proxy[1]
        print(proxy)

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
        }
        data = {
            "language": "zh_CN",
            "currency": "CNY",
            "flightCondition": f"index:0;depCode:{self.fromCity};arrCode:{self.toCity};depDate:{self.fromDate};"
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
        res = requests.get(url=url, headers=headers, params=data, verify=False, proxies=self.ip)
        if res.status_code == 200:
            return res.json()
        else:
            return {
                "status": 3,
                "msg": "查询航班失败"
            }

    def analysis_flight(self, flights):
        """
        :return:
        """
        flight_l = flights.get("data").get("flights")
        if flight_l:
            for flight01 in flight_l:
                for flight in flight01:
                    flights_ll = []
                    price_ll = []
                    fares = flight.get("fares")
                    segments = flight.get("segments")
                    if fares:
                        for fare in fares:
                            if fare.get("paxType") == "ADT":
                                price = {
                                    "extra": fare.get("productNo"),
                                    "proType": "",
                                    "cabin": fare.get("subClass"),
                                    "adtPrice": fare.get("ticketPrice"),
                                    "adtTax": fare.get("taxPrice"),
                                    "chdPrice": 0,
                                    "chdTax": 0,
                                    "infPrice": 0,
                                    "infTax": 0,
                                    "reducePrice": 0,
                                    "seats": int(fare.get("ticketLack")),
                                    "rule": ""
                                }
                                price_ll.append(price)
                            elif fare.get("paxType") == "CHD":
                                price = {
                                    "extra": fare.get("productNo"),
                                    "proType": "",
                                    "cabin": fare.get("subClass"),
                                    "adtPrice": 0,
                                    "adtTax": 0,
                                    "chdPrice": fare.get("ticketPrice"),
                                    "chdTax": fare.get("taxPrice"),
                                    "infPrice": 0,
                                    "infTax": 0,
                                    "reducePrice": 0,
                                    "seats": int(fare.get("ticketLack")),
                                    "rule": ""
                                }
                                price_ll.append(price)
                            else:
                                price = {
                                    "extra": fare.get("productNo"),
                                    "proType": "",
                                    "cabin": fare.get("subClass"),
                                    "adtPrice": 0,
                                    "adtTax": 0,
                                    "chdPrice": 0,
                                    "chdTax": 0,
                                    "infPrice": fare.get("ticketPrice"),
                                    "infTax": fare.get("taxPrice"),
                                    "reducePrice": 0,
                                    "seats": int(fare.get("ticketLack")),
                                    "rule": ""
                                }
                                price_ll.append(price)
                    else:
                        continue
                    if segments:
                        for segment in segments:
                            stop_air_ports = None if segment.get("stopoverCount") == 0 else segment.get("stopoverCount")
                            code_share = False if segment.get("codeShare") is False else segment.get("codeShare")
                            meals = segment.get("meal")
                            if meals:
                                meals = meals
                            else:
                                meals = ""
                            flig = {
                                "extra": segment.get("model"),
                                "carrier": segment.get("carrierAirlineCode"),
                                "flightNumber": segment.get("carrierAirlineCode") + segment.get("carrierFlightNo"),
                                "depAirport": segment.get("departAirportCode"),
                                "depTime": segment.get("departDate") + " " + segment.get("departTime"),
                                "arrAirport": segment.get("arrivalAirportCode"),
                                "arrTime": segment.get("arrivalDate") + " " + segment.get("arrivalTime"),
                                "stopAirports": stop_air_ports,
                                "codeShare": code_share,
                                "operatingCarrier": "",
                                "operatingFlightNo": "",
                                "meals": meals
                            }
                            flights_ll.append(flig)
                    else:
                        continue
                    self.journeys.append({
                        "flights": flights_ll,
                        "prices": price_ll
                    })
            if self.journeys:
                return {
                    "status": 0,
                    "msg": "success",
                    "journeys": self.journeys
                }
            else:
                return {
                    "status": 3,
                    "msg": "查询航班成功，该航班没有查询到任何机票价格信息"
                }
        else:
            return {
                "status": 3,
                "msg": "查询航班成功，该航段无所查询的航班"
            }

    def do_search(self):
        i = 0
        while i < 3:
            try:
                res = self.search_flight()
                if res.get("status") != 200:
                    res["index"] = "search_flight"
                    return res
                res_01 = self.analysis_flight(flights=res)
                if res_01.get("status") != 0:
                    res_01["index"] = "analysis_flight"
                    return res_01
                return res_01
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


random_to_city = ["TSN", "HAK", "DLC", "WUX"]

from_date = ["2020-06-15", "2020-06-11", "2020-06-12", "2020-06-18", "2020-07-14", "2020-07-02", "2020-07-19",
             "2020-07-12", "2020-06-26", "2020-06-23", "2020-06-21", "2020-06-03", "2020-06-22", "2020-06-12",
             "2020-06-06", "2020-06-12", "2020-06-19", "2020-07-08"]


def do_():
    Data = {
        "tripType": 1,
        "fromCity": "CSX",
        "toCity": "HAK",
        "fromDate": "2020-05-27",
        "retDate": "",
        "flightNo": "",
        "cabin": "",
        "adultNum": 1,
        "childNum": 0,
        "infantNum": 0,
    }
    return Data



if __name__ == "__main__":
    print(do_())

