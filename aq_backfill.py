from AQ.AQ_backfill import do_do_backfill
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


# http://192.168.0.173:9004/backfill_aq
@app.route('/backfill_aq', methods=['POST', 'GET'])
def search_aq():
    params = json.loads(request.get_data(as_text=True))
    print(params)
    ret = do_do_backfill(params=params)
    return json.dumps(ret)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9004, threaded=True)
