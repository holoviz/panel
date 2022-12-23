import time
import numpy as np
import logging
from datetime import datetime as dt


def blocking_computation(x: float) -> float:
    start = dt.now()
    print("starting blocking_computation", start)
    samples = []
    for _ in range(1000):
        time.sleep(0.001)
        samples.append(np.random.normal(loc=1.0, scale=1.0))
    result = x + int(np.ceil(np.mean(samples)))
    end = dt.now()
    print("ending blocking_computation", end)
    print("duration", (end-start))
    return result