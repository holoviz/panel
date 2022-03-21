import asyncio

import param


def async_execute(func):
    event_loop = asyncio.get_running_loop()
    if event_loop.is_running():
        event_loop.call_soon(func)
    else:
        event_loop.run_until_complete(func())
    return

param.parameterized.async_executor = async_execute


def serve(*args, **kwargs):
    """
    Stub to replace Tornado based serve function.
    """
    raise RuntimeError('Cannot serve application in pyodide context.')
