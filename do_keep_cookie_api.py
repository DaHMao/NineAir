from AQ.AQ_login import Login
import json
from flask import Flask, request
import traceback
from aq_log.Journal_class import Journal

app = Flask(__name__)


@app.route("/")
def dd():
    print("hello")
    return "hello"


# http://192.168.0.173:9002/keep_cookie_aq
@app.route('/keep_cookie_aq', methods=['POST', 'GET'])
def keep_cookie_aq():
    params = json.loads(request.get_data(as_text=True))
    print(params)
    try:
        ret = Login(data=params).do_keep_session()
        print(ret)
        resp = {
            "请求数据": params,
            "响应数据": ret
        }
        if ret.get("state") == 1:
            Journal().save_journal_keep_cookie(massage=json.dumps(resp), level="warn")
    except Exception as e:
        print(e)
        ret = {'state': 1, 'msg': traceback.format_exc()}
        resp = {
            "请求数据": params,
            "响应数据": ret
        }
        Journal().save_journal_keep_cookie(massage=json.dumps(resp), level="error")
    return json.dumps(ret)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9002, threaded=True)
