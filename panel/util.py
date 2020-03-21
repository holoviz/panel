"""
Various general utilities used in the panel codebase.
"""
from __future__ import absolute_import, division, unicode_literals

import datetime as dt
import inspect
import numbers
import os
import re
import sys

from collections import defaultdict, OrderedDict
from datetime import datetime
from six import string_types

try:  # python >= 3.3
    from collections.abc import MutableSequence, MutableMapping
except ImportError:
    from collections import MutableSequence, MutableMapping

import param
import numpy as np

datetime_types = (np.datetime64, dt.datetime, dt.date)

if sys.version_info.major > 2:
    unicode = str
    from html import escape as _escape
else:
    from xml.sax.saxutils import quoteattr


html_escape_table = {
    '"': "&quot;",
    "'": "&#x27;"
}


def escape(string):
    """
    Temporary wrapper around HTML escaping to allow using Div model
    during static png exports.
    """
    from .io import state

    if state._html_escape:
        if sys.version_info.major == 2:
            return quoteattr(string, html_escape_table)[1:-1]
        else:
            return _escape(string)
    else:
        return string


def isfile(path):
    """Safe version of os.path.isfile robust to path length issues on Windows"""
    try:
        return os.path.isfile(path)
    except ValueError: # path too long for Windows
        return False


def isurl(obj, formats):
    if not isinstance(obj, string_types):
        return False
    lower_string = obj.lower()
    return (
        lower_string.startswith('http://')
        or lower_string.startswith('https://')
    ) and any(lower_string.endswith('.'+fmt) for fmt in formats)


def is_dataframe(obj):
    if 'pandas' not in sys.modules:
        return False
    import pandas as pd
    return isinstance(obj, pd.DataFrame)


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
    if isinstance(value, np.ndarray):
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
