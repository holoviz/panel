"""
Various general utilities used in the panel codebase.
"""
import base64
import datetime as dt
import inspect
import json
import numbers
import os
import re
import sys
import urllib.parse as urlparse

from collections.abc import MutableSequence, MutableMapping
from collections import defaultdict, OrderedDict
from contextlib import contextmanager
from datetime import datetime
from distutils.version import LooseVersion
from functools import partial
from html import escape # noqa
from importlib import import_module
from six import string_types

import bokeh
import param
import numpy as np

datetime_types = (np.datetime64, dt.datetime, dt.date)

if sys.version_info.major > 2:
    unicode = str

bokeh_version = LooseVersion(bokeh.__version__)


def isfile(path):
    """Safe version of os.path.isfile robust to path length issues on Windows"""
    try:
        return os.path.isfile(path)
    except ValueError: # path too long for Windows
        return False


def isurl(obj, formats):
    if not isinstance(obj, string_types):
        return False
    lower_string = obj.lower().split('?')[0].split('#')[0]
    return (
        lower_string.startswith('http://')
        or lower_string.startswith('https://')
    ) and (formats is None or any(lower_string.endswith('.'+fmt) for fmt in formats))


def is_dataframe(obj):
    if 'pandas' not in sys.modules:
        return False
    import pandas as pd
    return isinstance(obj, pd.DataFrame)


def is_series(obj):
    if 'pandas' not in sys.modules:
        return False
    import pandas as pd
    return isinstance(obj, pd.Series)


def hashable(x):
    if isinstance(x, MutableSequence):
        return tuple(x)
    elif isinstance(x, MutableMapping):
        return tuple([(k,v) for k,v in x.items()])
    else:
        return x


def isIn(obj, objs):
    """
    Checks if the object is in the list of objects safely.
    """
    for o in objs:
        if o is obj:
            return True
        try:
            if o == obj:
                return True
        except Exception:
            pass
    return False


def indexOf(obj, objs):
    """
    Returns the index of an object in a list of objects. Unlike the
    list.index method this function only checks for identity not
    equality.
    """
    for i, o in enumerate(objs):
        if o is obj:
            return i
        try:
            if o == obj:
                return i
        except Exception:
            pass
    raise ValueError('%s not in list' % obj)


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
    match = re.findall(r'\D+(\d{5,})', name)
    return name[:name.index(match[0])] if match else name


def unicode_repr(obj):
    """
    Returns a repr without the unicode prefix.
    """
    if sys.version_info.major == 2 and isinstance(obj, unicode):
        return repr(obj)[1:]
    return repr(obj)


def recursive_parameterized(parameterized, objects=None):
    """
    Recursively searches a Parameterized object for other Parmeterized
    objects.
    """
    objects = [] if objects is None else objects
    objects.append(parameterized)
    for _, p in parameterized.param.get_param_values():
        if isinstance(p, param.Parameterized) and not any(p is o for o in objects):
            recursive_parameterized(p, objects)
    return objects


def abbreviated_repr(value, max_length=25, natural_breaks=(',', ' ')):
    """
    Returns an abbreviated repr for the supplied object. Attempts to
    find a natural break point while adhering to the maximum length.
    """
    if isinstance(value, list):
        vrepr = '[' + ', '.join([abbreviated_repr(v) for v in value]) + ']'
    if isinstance(value, param.Parameterized):
        vrepr = type(value).__name__
    else:
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


def param_reprs(parameterized, skip=None):
    """
    Returns a list of reprs for parameters on the parameterized object.
    Skips default and empty values.
    """
    cls = type(parameterized).__name__
    param_reprs = []
    for p, v in sorted(parameterized.param.get_param_values()):
        default = parameterized.param[p].default
        equal = v is default
        if not equal:
            if isinstance(v, np.ndarray):
                if isinstance(default, np.ndarray):
                    equal = np.array_equal(v, default, equal_nan=True)
                else:
                    equal = False
            else:
                try:
                    equal = bool(v==default)
                except Exception:
                    equal = False

        if equal: continue
        elif v is None: continue
        elif isinstance(v, string_types) and v == '': continue
        elif isinstance(v, list) and v == []: continue
        elif isinstance(v, dict) and v == {}: continue
        elif (skip and p in skip) or (p == 'name' and v.startswith(cls)): continue
        else: v = abbreviated_repr(v)
        param_reprs.append('%s=%s' % (p, v))
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


def isdatetime(value):
    """
    Whether the array or scalar is recognized datetime type.
    """
    if is_series(value) and len(value):
        return isinstance(value.iloc[0], datetime_types)
    elif isinstance(value, np.ndarray):
        return (value.dtype.kind == "M" or
                (value.dtype.kind == "O" and len(value) and
                 isinstance(value[0], datetime_types)))
    elif isinstance(value, list):
        return all(isinstance(d, datetime_types) for d in value)
    else:
        return isinstance(value, datetime_types)

def value_as_datetime(value):
    """
    Retrieve the value tuple as a tuple of datetime objects.
    """
    if isinstance(value, numbers.Number):
        value = datetime.utcfromtimestamp(value / 1000)
    return value


def value_as_date(value):
    if isinstance(value, numbers.Number):
        value = datetime.utcfromtimestamp(value / 1000).date()
    elif isinstance(value, datetime):
        value = value.date()
    return value


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def parse_query(query):
    """
    Parses a url query string, e.g. ?a=1&b=2.1&c=string, converting
    numeric strings to int or float types.
    """
    query = dict(urlparse.parse_qsl(query[1:]))
    for k, v in list(query.items()):
        if v.isdigit():
            query[k] = int(v)
        elif is_number(v):
            query[k] = float(v)
        elif v.startswith('[') or v.startswith('{'):
            query[k] = json.loads(v)
    return query


def base64url_encode(input):
    if isinstance(input, str):
        input = input.encode("utf-8")
    encoded = base64.urlsafe_b64encode(input).decode('ascii')
    # remove padding '=' chars that cause trouble
    return str(encoded.rstrip('='))


def base64url_decode(input):
    if isinstance(input, str):
        input = input.encode("ascii")

    rem = len(input) % 4

    if rem > 0:
        input += b"=" * (4 - rem)

    return base64.urlsafe_b64decode(input)


class classproperty(object):

    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


def url_path(url):
    return os.path.join(*os.path.join(*url.split('//')[1:]).split('/')[1:])


# This functionality should be contributed to param
# See https://github.com/holoviz/param/issues/379
@contextmanager
def edit_readonly(parameterized):
    """
    Temporarily set parameters on Parameterized object to readonly=False
    to allow editing them.
    """
    params = parameterized.param.objects("existing").values()
    readonlys = [p.readonly for p in params]
    constants = [p.constant for p in params]
    for p in params:
        p.readonly = False
        p.constant = False
    try:
        yield
    except Exception:
        raise
    finally:
        for (p, readonly) in zip(params, readonlys):
            p.readonly = readonly
        for (p, constant) in zip(params, constants):
            p.constant = constant


def lazy_load(module, model, notebook=False):
    if module in sys.modules:
        return getattr(sys.modules[module], model)
    if notebook:
        ext = module.split('.')[-1]
        param.main.param.warning(f'{model} was not imported on instantiation '
                                 'and may not render in a notebook. Restart '
                                 'the notebook kernel and ensure you load '
                                 'it as part of the extension using:'
                                 f'\n\npn.extension(\'{ext}\')\n')
    return getattr(import_module(module), model)


def updating(fn):
    def wrapped(self, *args, **kwargs):
        updating = self._updating
        self._updating = True
        try:
            fn(self, *args, **kwargs)
        finally:
            self._updating = updating
    return wrapped


def clone_model(bokeh_model, include_defaults=False, include_undefined=False):
    properties = bokeh_model.properties_with_values(
        include_defaults=include_defaults, include_undefined=include_undefined
    )
    return type(bokeh_model)(**properties)


def doc_event_obj(doc):
    """
    Temporary helper for Bokeh 2.3/2.4 compatibility
    """
    return doc.callbacks if bokeh_version >= '2.4' and hasattr(doc, 'callbacks') else doc


def function_name(func):
    """
    Returns the name of a function (or its string repr)
    """
    while isinstance(func, partial):
        func = func.func
    if hasattr(func, '__name__'):
        return func.__name__
    return str(func)
