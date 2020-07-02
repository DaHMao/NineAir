from AQ.AQ_search import Search
import json
from flask import Flask, request
import traceback
from aq_log.Journal_class import Journal
import time

app = Flask(__name__)


@app.route("/")
def dd():
    print("hello")
    return "hello"


# http://192.168.0.173:9003/search_aq
@app.route('/search_aq', methods=['POST', 'GET'])
def search_aq():
    start_time = time.time()
    params = json.loads(request.get_data(as_text=True))
    print(params)
    try:
        ret = Search(data=params).do_search()
        print(ret)
        end_time = time.time()
        resp = {
            "请求数据": params,
            "响应数据": ret,
            "询价耗时": str(end_time - start_time)
        }
        if ret.get("status") in (0, 11):
            Journal().save_journal_search(massage=json.dumps(resp), field1=str(end_time - start_time))
        else:
            Journal().save_journal_search(massage=json.dumps(resp), level="warn")
    except Exception as e:
        print(e)
        ret = {'status': 5, 'msg': traceback.format_exc()}
        resp = {
            "请求数据": params,
            "响应数据": ret
        }
        Journal().save_journal_search(massage=json.dumps(resp), level="error")
    return json.dumps(ret)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9003, threaded=True)
