
import os

from flask import Flask, request
from waitress import serve

import helpers
import position

CUR_DIR = os.path.abspath(os.path.join(__file__, ".."))

os.chdir(CUR_DIR)

app = Flask(__name__)


@app.route('/prestart/', methods=["POST"])
@helpers.crossdomain(origin='*')
def prestart():
    request_data = request.form

    up = position.UserPosition.from_form(request_data)
    with helpers.db() as conn:
        up.to_db(conn)
    return ""


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=6081)
