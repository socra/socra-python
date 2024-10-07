import threading
from datetime import datetime, timedelta
from functools import wraps


def debounce(wait_time):
    """
    wait_time: int - the time in seconds to wait before calling the function

    Decorator that will debounce a function so that it is called after wait_time seconds
    If it is called multiple times, will wait for the last call to be debounced and run only this one.

    See https://stackoverflow.com/questions/61476962/python-decorator-for-debouncing-including-function-arguments
    """

    def decorator(function):
        def debounced(*args, **kwargs):
            def call_function():
                debounced._timer = None
                return function(*args, **kwargs)

            # if we already have a call to the function currently waiting to be executed, reset the timer
            if debounced._timer is not None:
                debounced._timer.cancel()

            # after wait_time, call the function provided to the decorator with its arguments
            debounced._timer = threading.Timer(wait_time, call_function)
            debounced._timer.start()

        debounced._timer = None
        return debounced

    return decorator


class throttle(object):
    """
    Decorator that prevents a function from being called more than once every
    time period.
    To create a function that cannot be called more than once a minute:
        @throttle(minutes=1)
        def my_fun():
            pass
    """

    def __init__(self, seconds=0, minutes=0, hours=0):
        self.throttle_period = timedelta(seconds=seconds, minutes=minutes, hours=hours)
        self.time_of_last_call = datetime.min

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            now = datetime.now()
            time_since_last_call = now - self.time_of_last_call

            if time_since_last_call > self.throttle_period:
                self.time_of_last_call = now
                return fn(*args, **kwargs)

        return wrapper
