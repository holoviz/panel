from __future__ import absolute_import, division, unicode_literals

import re
import os
import io
import json
import sys
import inspect
import numbers
import hashlib
import threading
import textwrap

from collections import defaultdict, MutableSequence, MutableMapping, OrderedDict
from datetime import datetime
from six import string_types

import param

from bokeh.document import Document
from bokeh.models import Model, Box

# Global variables
CUSTOM_MODELS = {}

if sys.version_info.major > 2:
    unicode = str


def load_compiled_models(custom_model, implementation):
    """
    Custom hook to load cached implementation of custom models.
    """
    compiled = old_hook(custom_model, implementation)
    if compiled is not None:
        return compiled

    model = CUSTOM_MODELS.get(custom_model.full_name)
    if model is None:
        return
    ts_file = model.__implementation__
    json_file = ts_file.replace('.ts', '.json')
    if not os.path.isfile(json_file):
        return
    with io.open(ts_file, encoding="utf-8") as f:
        code = f.read()
    with io.open(json_file, encoding="utf-8") as f:
        compiled = json.load(f)
    hashed = hashlib.sha256(code.encode('utf-8')).hexdigest()
    if compiled['hash'] == hashed:
        return AttrDict(compiled)
    return None


try:
    from bokeh.util.compiler import AttrDict, get_cache_hook, set_cache_hook
    old_hook = get_cache_hook()
    set_cache_hook(load_compiled_models)
except:
    pass


def hashable(x):
    if isinstance(x, MutableSequence):
        return tuple(x)
    elif isinstance(x, MutableMapping):
        return tuple([(k,v) for k,v in x.items()])
    else:
        return x


def as_unicode(obj):
    """
    Safely casts any object to unicode including regular string
    (i.e. bytes) types in python 2.
    """
    if sys.version_info.major < 3 and isinstance(obj, str):
        obj = obj.decode('utf-8')
    return unicode(obj)


def param_name(name):
    """
    Removes the integer id from a Parameterized class name.
    """
    match = re.match('(.)+(\d){5}', name)
    return name[:-5] if match else name


def unicode_repr(obj):
    """
    Returns a repr without the unicode prefix.
    """
    if sys.version_info.major == 2 and isinstance(obj, unicode):
        return repr(obj)[1:]
    return repr(obj)


def abbreviated_repr(value, max_length=25, natural_breaks=(',', ' ')):
    """
    Returns an abbreviated repr for the supplied object. Attempts to
    find a natural break point while adhering to the maximum length.
    """
    vrepr = repr(value)
    if len(vrepr) > max_length:
        # Attempt to find natural cutoff point
        abbrev = vrepr[max_length//2:]
        natural_break = None
        for brk in natural_breaks:
            if brk in abbrev:
                natural_break = abbrev.index(brk) + max_length//2
                break
        if natural_break and natural_break < max_length:
            max_length = natural_break + 1

        end_char = ''
        if isinstance(value, list):
            end_char = ']'
        elif isinstance(value, OrderedDict):
            end_char = '])'
        elif isinstance(value, (dict, set)):
            end_char = '}'
        return vrepr[:max_length+1] + '...' + end_char
    return vrepr


def param_reprs(parameterized, skip=[]):
    """
    Returns a list of reprs for parameters on the parameterized object.
    Skips default and empty values.
    """
    cls = type(parameterized).__name__
    param_reprs = []
    for p, v in sorted(parameterized.get_param_values()):
        if v is parameterized.param[p].default: continue
        elif v is None: continue
        elif isinstance(v, string_types) and v == '': continue
        elif isinstance(v, list) and v == []: continue
        elif isinstance(v, dict) and v == {}: continue
        elif p in skip or (p == 'name' and v.startswith(cls)): continue
        param_reprs.append('%s=%s' % (p, abbreviated_repr(v)))
    return param_reprs


def full_groupby(l, key=lambda x: x):
    """
    Groupby implementation which does not require a prior sort
    """
    d = defaultdict(list)
    for item in l:
        d[key(item)].append(item)
    return d.items()


def get_method_owner(meth):
    """
    Returns the instance owning the supplied instancemethod or
    the class owning the supplied classmethod.
    """
    if inspect.ismethod(meth):
        if sys.version_info < (3,0):
            return meth.im_class if meth.im_self is None else meth.im_self
        else:
            return meth.__self__


def is_parameterized(obj):
    """
    Whether an object is a Parameterized class or instance.
    """
    return (isinstance(obj, param.Parameterized) or
            (isinstance(obj, type) and issubclass(obj, param.Parameterized)))


def value_as_datetime(value):
    """
    Retrieve the value tuple as a tuple of datetime objects.
    """
    if isinstance(value, numbers.Number):
        value = datetime.utcfromtimestamp(value / 1000)
    return value




class StoppableThread(threading.Thread):
    """Thread class with a stop() method."""

    def __init__(self, io_loop=None, timeout=1000, **kwargs):
        from tornado import ioloop
        super(StoppableThread, self).__init__(**kwargs)
        self._stop_event = threading.Event()
        self.io_loop = io_loop
        self._cb = ioloop.PeriodicCallback(self._check_stopped, timeout)
        self._cb.start()

    def _check_stopped(self):
        if self.stopped:
            self._cb.stop()
            self.io_loop.stop()

    def stop(self):
        self._stop_event.set()

    @property
    def stopped(self):
        return self._stop_event.is_set()


################################
# Display and update utilities #
################################


def bokeh_repr(obj, depth=0, ignored=['children', 'text', 'name', 'toolbar', 'renderers', 'below', 'center', 'left', 'right']):
    from .viewable import Viewable
    if isinstance(obj, Viewable):
        obj = obj._get_root(Document())

    r = ""
    cls = type(obj).__name__
    properties = sorted(obj.properties_with_values(False).items())
    props = []
    for k, v in properties:
        if k in ignored:
            continue
        if isinstance(v, Model):
            v = '%s()' % type(v).__name__
        else:
            v = repr(v)
        if len(v) > 30:
            v = v[:30] + '...'
        props.append('%s=%s' % (k, v))
    props = ', '.join(props)
    if isinstance(obj, Box):
        r += '{cls}(children=[\n'.format(cls=cls)
        for obj in obj.children:
            r += textwrap.indent(bokeh_repr(obj, depth=depth+1) + ',\n', '  ')
        r += '], %s)' % props
    else:
        r += '{cls}({props})'.format(cls=cls,  props=props)
    return r
