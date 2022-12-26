# tasks.py
from datetime import datetime as dt

import numpy as np


def _fib(n):
    if n < 2:
        return n
    else:
        return _fib(n - 1) + _fib(n - 2)


def fibonacci(n):
    start = dt.now()
    print(start, "start", n)
    result = _fib(n)
    end = dt.now()
    print(end, "end", (end-start).seconds, n, result)
    return result
