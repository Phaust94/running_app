
import os
import pytz
import datetime
import json

from flask import Flask, request
from waitress import serve

from helpers import crossdomain

CUR_DIR = os.path.abspath(os.path.join(__file__, ".."))

os.chdir(CUR_DIR)

app = Flask(__name__)


@app.route('/prestart/', methods=["GET"])
@crossdomain(origin='*')
def prestart():
    user_id = int(request.args["user_id"])
    # current_time = request.args["curr_time"]

    return json.dumps({"Success": 1})


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=6081)
