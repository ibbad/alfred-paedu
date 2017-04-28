"""
Decorators for web application functionality.
"""
from functools import wraps
from app.exceptions import TimeoutError
import errno
import os
import signal
from requests import ConnectionError
from flask import jsonify

def handle_connection_error(function):

    @wraps(function)
    def decorated(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except ConnectionError as e:
            url = str(e)
            return jsonify({"status": "Backend not found",
                            "ErrorMessage": url})

    return decorated

def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result
        return wraps(func)(wrapper)
    return decorator
