from contextlib import contextmanager
from cProfile import Profile
from functools import wraps

from .state import state

@contextmanager
def profile_ctx(engine='pyinstrument'):
    if engine == 'pyinstrument':
        from pyinstrument import Profiler
        prof = Profiler()
        prof.start()
    elif engine == 'snakeviz':
        prof = Profile()
        prof.enable()
    elif engine is None:
        pass
    sessions = []
    yield sessions
    if engine == 'pyinstrument':
        sessions.append(prof.stop())
    elif engine == 'snakeviz':
        prof.disable()
        sessions.append(prof)


def profile(name, engine='pyinstrument'):
    """
    A decorator which may be added to any function to record profiling
    output.
    """
    if not isinstance(name, str):
        raise ValueError("Profiler must be given a name.")
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if not state.curdoc or state.curdoc in state._launching:
                return func(*args, **kwargs)
            with profile_ctx(engine) as sessions:
                ret = func(*args, **kwargs)
            state._profiles[(name, engine)] += sessions
            state.param.trigger('_profiles')
            return ret
        return wrapped
    return wrapper
