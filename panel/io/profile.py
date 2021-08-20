from functools import wraps

from .state import state

def profile(name):
    """
    A decorator which may be added to any function to record profiling
    output.
    """
    if not isinstance(name, str):
        raise ValueError("Profiler must be given a name, i.e.")
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            from pyinstrument import Profiler
            if not state.curdoc or state.curdoc in state._launching:
                return func(*args, **kwargs)
            with Profiler() as p:
                ret = func(*args, **kwargs)
            state._user_profiles[name].append(p.last_session)
            state.param.trigger('_user_profiles')
            return ret
        return wrapped
    return wrapper
