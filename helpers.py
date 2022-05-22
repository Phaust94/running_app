from datetime import timedelta
from functools import update_wrapper
import binascii
import json
import typing
import contextlib
from sqlite3 import connect

from flask import make_response, request, current_app
import blowfish

import constants

__all__ = [
    "crossdomain",
    "db",
    "decrypt_qeng_data",
]


def crossdomain(origin=None, methods=None, headers=None, max_age=21600,
                attach_to_all=True, automatic_options=True):
    """Decorator function that allows crossdomain requests.
      Courtesy of
      https://blog.skyred.fi/articles/better-crossdomain-snippet-for-flask.html
    """
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    # use str instead of basestring if using Python 3.x
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    # use str instead of basestring if using Python 3.x
    if not isinstance(origin, str):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        """ Determines which methods are allowed
        """
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        """The decorator function
        """
        def wrapped_function(*args, **kwargs):
            """Caries out the actual cross domain code
            """
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['Access-Control-Allow-Credentials'] = 'true'
            h['Access-Control-Allow-Headers'] = \
                "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


def decrypt_qeng_data(
        data: str,
        key: str,
) -> typing.Dict[str, typing.Union[str, int]]:
    data = binascii.unhexlify(data)
    cipher = blowfish.Cipher(key.encode())
    data_decrypted = b"".join(cipher.decrypt_ecb(data))
    data_decrypted = data_decrypted.rstrip(b'\x00')
    data_json = json.loads(data_decrypted)
    return data_json


@contextlib.contextmanager
def db():
    conn = connect(constants.DB_PATH)
    try:
        yield conn
    finally:
        conn.close()
    return None