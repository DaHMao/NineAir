from AQ.AQ_search import Search
import json
from flask import Flask, request
import traceback
from aq_log.Journal_class import Journal
from aq_log.loghelper import __write_log__

app = Flask(__name__)


@app.route("/")
def dd():
    print("hello")
    return "hello"


# http://192.168.0.173:11104/search_aq
@app.route('/search_aq', methods=['POST', 'GET'])
def register_tc():
    log = ''
    params = json.loads(request.get_data(as_text=True))
    print(params)
    try:
        ret = Search(data=params).do_search()
        print(ret)
        resp = {
            "请求数据": params,
            "响应数据": ret
        }
        Journal().save_journal_search(massage=json.dumps(resp))
    except Exception:
        ret = {'code': 500, 'msg': traceback.format_exc()}
        resp = {
            "请求数据": params,
            "响应数据": ret
        }
        Journal().save_journal_search(massage=json.dumps(resp), level="error")
    log = log + str(ret) + '\n'
    __write_log__(log, tag="_search_")
    return json.dumps(ret)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=11104, threaded=True)
