"""
Various general utilities used in the panel codebase.
"""
from __future__ import annotations

import ast
import asyncio
import base64
import datetime as dt
import json
import logging
import numbers
import os
import pathlib
import re
import sys
import urllib.parse as urlparse

from collections import OrderedDict, defaultdict
from collections.abc import MutableMapping, MutableSequence
from datetime import datetime
from functools import partial
from html import escape  # noqa
from importlib import import_module
from typing import Any, AnyStr

import bokeh
import numpy as np
import param

from bokeh.core.has_props import _default_resolver
from bokeh.model import Model
from packaging.version import Version

from .checks import (  # noqa
    datetime_types, is_dataframe, is_holoviews, is_number, is_parameterized,
    is_series, isdatetime, isfile, isIn, isurl,
)
from .parameters import (  # noqa
    edit_readonly, extract_dependencies, get_method_owner,
    recursive_parameterized,
)

log = logging.getLogger('panel.util')

bokeh_version = Version(Version(bokeh.__version__).base_version)
BOKEH_GE_3_6 = bokeh_version >= Version('3.6')

PARAM_NAME_PATTERN = re.compile(r'^.*\d{5}$')

class LazyHTMLSanitizer:
    """
    Wraps bleach.sanitizer.Cleaner lazily importing it on the first
    call to the clean method.
    """

    def __init__(self, **kwargs):
        self._cleaner = None
        self._kwargs = kwargs

    def clean(self, text):
        if self._cleaner is None:
            import bleach
            self._cleaner = bleach.sanitizer.Cleaner(**self._kwargs)
        return self._cleaner.clean(text)

HTML_SANITIZER = LazyHTMLSanitizer(strip=True)


def hashable(x):
    if isinstance(x, MutableSequence):
        return tuple(x)
    elif isinstance(x, MutableMapping):
        return tuple([(k,v) for k,v in x.items()])
    else:
        return x

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
    raise ValueError(f'{obj} not in list')


def param_name(name: str) -> str:
    """
    Removes the integer id from a Parameterized class name.
    """
    match = re.findall(r'\D+(\d{5,})', name)
    return name[:name.index(match[0])] if match else name


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
    for p, v in sorted(parameterized.param.values().items()):
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
        elif isinstance(v, str) and v == '': continue
        elif isinstance(v, list) and v == []: continue
        elif isinstance(v, dict) and v == {}: continue
        elif (skip and p in skip) or (p == 'name' and v.startswith(cls)): continue
        else: v = abbreviated_repr(v)
        param_reprs.append(f'{p}={v}')
    return param_reprs


def full_groupby(l, key=lambda x: x):
    """
    Groupby implementation which does not require a prior sort
    """
    d = defaultdict(list)
    for item in l:
        d[key(item)].append(item)
    return d.items()


def value_as_datetime(value):
    """
    Retrieve the value tuple as a tuple of datetime objects.
    """
    if isinstance(value, numbers.Number):
        value = datetime.fromtimestamp(value / 1000, tz=dt.timezone.utc).replace(tzinfo=None)
    return value


def value_as_date(value):
    if isinstance(value, numbers.Number):
        value = datetime.fromtimestamp(value / 1000, tz=dt.timezone.utc).replace(tzinfo=None).date()
    elif isinstance(value, datetime):
        value = value.date()
    return value


def datetime_as_utctimestamp(value):
    """
    Converts a datetime to a UTC timestamp used by Bokeh internally.
    """
    return value.replace(tzinfo=dt.timezone.utc).timestamp() * 1000


def parse_query(query: str) -> dict[str, Any]:
    """
    Parses a url query string, e.g. ?a=1&b=2.1&c=string, converting
    numeric strings to int or float types.
    """
    query_dict = dict(urlparse.parse_qsl(query[1:]))
    parsed_query: dict[str, Any] = {}
    for k, v in query_dict.items():
        if v.isdigit():
            parsed_query[k] = int(v)
        elif is_number(v):
            parsed_query[k] = float(v)
        elif v.startswith(('[', '{')):
            try:
                parsed_query[k] = json.loads(v)
            except Exception:
                try:
                    parsed_query[k] = ast.literal_eval(v)
                except Exception:
                    log.warning(
                        f'Could not parse value {v!r} of query parameter {k}. '
                        'Parameter will be ignored.'
                    )
        elif v.lower() in ("true", "false"):
            parsed_query[k] = v.lower() == "true"
        else:
            parsed_query[k] = v
    return parsed_query


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


def decode_token(token: str, signed: bool = True) -> dict[str, Any]:
    """
    Decodes a signed or unsigned JWT token.
    """
    if signed and "." in token:
        signing_input, _ = token.encode('utf-8').rsplit(b".", 1)
        _, payload_segment = signing_input.split(b".", 1)
    else:
        payload_segment = token.encode('ascii')
    return json.loads(base64url_decode(payload_segment).decode('utf-8'))


class classproperty:

    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


def url_path(url: str) -> str:
    """
    Strips the protocol and domain from a URL returning just the path.
    """
    subpaths = url.split('//')[1:]
    return '/'.join('/'.join(subpaths).split('/')[1:])


def lazy_load(module, model, notebook=False, root=None, ext=None):
    from ..config import panel_extension as extension
    from ..io.state import state
    external_modules = {
        module: ext for ext, module in extension._imports.items()
    }
    ext = ext or module.split('.')[-1]
    ext_name = external_modules[module]
    loaded_extensions = state._extensions
    loaded = loaded_extensions is None or ext_name in loaded_extensions
    if module in sys.modules and loaded:
        model_cls = getattr(sys.modules[module], model)
        if f'{model_cls.__module__}.{model}' not in Model.model_class_reverse_map:
            _default_resolver.add(model_cls)
        return model_cls

    if notebook:
        param.main.param.warning(
            f'{model} was not imported on instantiation and may not '
            'render in a notebook. Restart the notebook kernel and '
            'ensure you load it as part of the extension using:'
            f'\n\npn.extension(\'{ext}\')\n'
        )
    elif not loaded and state._is_launching:
        # If we are still launching the application it is not too late
        # to automatically load the extension and therefore ensure it
        # is included in the resources added to the served page
        param.main.param.warning(
            f'pn.extension was initialized but {ext!r} extension was not '
            'loaded. Since the application is still launching the extension '
            'was loaded automatically but we strongly recommend you load '
            'the extension explicitly with the following argument(s):'
            f'\n\npn.extension({ext!r})\n'
        )
        if loaded_extensions is None:
            state._extensions_[state.curdoc] = [ext_name]
        else:
            loaded_extensions.append(ext_name)
    elif not loaded:
        param.main.param.warning(
            f'pn.extension was initialized but {ext!r} extension was not '
            'loaded. In order for the required resources to be initialized '
            'ensure the extension is loaded with the following argument(s):'
            f'\n\npn.extension({ext!r})\n'
        )
    elif root is not None and root.ref['id'] in state._views:
        param.main.param.warning(
            f'{model} was not imported on instantiation may not '
            'render in the served application. Ensure you add the '
            'following to the top of your application:'
            f'\n\npn.extension(\'{ext}\')\n'
        )
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


def function_name(func) -> str:
    """
    Returns the name of a function (or its string repr)
    """
    while isinstance(func, partial):
        func = func.func
    if hasattr(func, '__name__'):
        return func.__name__
    return str(func)


_period_regex = re.compile(r'((?P<weeks>\d+?)w)?((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?\.?\d*?)s)?')

def parse_timedelta(time_str: str) -> dt.timedelta | None:
    parts = _period_regex.match(time_str)
    if not parts:
        return None
    parts_dict = parts.groupdict()
    time_params = {}
    for (name, p) in parts_dict.items():
        if p:
            time_params[name] = float(p)
    return dt.timedelta(**time_params)


def fullpath(path: AnyStr | os.PathLike) -> str:
    """
    Expanduser and then abspath for a given path.
    """
    if '://' in str(path):
        return str(path)
    return str(os.path.abspath(os.path.expanduser(path)))


def base_version(version: str) -> str:
    """Extract the final release and if available pre-release (alpha, beta,
    release candidate) segments of a PEP440 version, defined with three
    components (major.minor.micro).

    Useful to avoid nbsite/sphinx to display the documentation HTML title
    with a not so informative and rather ugly long version (e.g.
    ``0.13.0a19.post4+g0695e214``). Use it in ``conf.py``::

        version = release = base_version(package.__version__)

    Return the version passed as input if no match is found with the pattern.
    """
    # look at the start for e.g. 0.13.0, 0.13.0rc1, 0.13.0a19, 0.13.0b10
    pattern = r"([\d]+\.[\d]+\.[\d]+(?:a|rc|b)?[\d]*)"
    match = re.match(pattern, version)
    if match:
        return match.group()
    else:
        return version


def relative_to(path, other_path):
    try:
        pathlib.Path(path).relative_to(other_path)
        return True
    except Exception:
        return False


def flatten(line):
    """
    Flatten an arbitrarily nested sequence.

    Inspired by: pd.core.common.flatten

    Parameters
    ----------
    line : sequence
        The sequence to flatten

    Notes
    -----
    This only flattens list, tuple, and dict sequences.

    Returns
    -------
    flattened : generator
    """
    for element in line:
        if any(isinstance(element, tp) for tp in (list, tuple, dict)):
            yield from flatten(element)
        else:
            yield element


def styler_update(styler, new_df):
    """
    Updates the todo items on a pandas Styler object to apply to a new
    DataFrame.

    Parameters
    ----------
    styler: pandas.io.formats.style.Styler
      Styler objects
    new_df: pd.DataFrame
      New DataFrame to update the styler to do items

    Returns
    -------
    todos: list
    """
    todos = []
    for todo in styler._todo:
        if not isinstance(todo, tuple):
            todos.append(todo)
            continue
        ops = []
        for op in todo:
            if not isinstance(op, tuple):
                ops.append(op)
                continue
            op_fn = str(op[0])
            if ('_background_gradient' in op_fn or '_bar' in op_fn) and op[1] in (0, 1):
                if isinstance(op[2], list):
                    applies = op[2]
                else:
                    applies = np.array([
                        new_df[col].dtype.kind in 'uif' for col in new_df.columns
                    ])
                    if len(op[2]) == len(applies):
                        applies = np.logical_and(applies, op[2])
                op = (op[0], op[1], applies)
            ops.append(op)
        todo = tuple(ops)
        todos.append(todo)
    return todos


def try_datetime64_to_datetime(value):
    if isinstance(value, np.datetime64):
        value = value.astype('datetime64[ms]').astype(datetime)
    return value


async def to_async_gen(sync_gen):
    done = object()

    def safe_next():
        # Converts StopIteration to a sentinel value to avoid:
        # TypeError: StopIteration interacts badly with generators and cannot be raised into a Future
        try:
            return next(sync_gen)
        except StopIteration:
            return done

    while True:
        value = await asyncio.to_thread(safe_next)
        if value is done:
            break
        yield value

def unique_iterator(seq):
    """
    Returns an iterator containing all non-duplicate elements
    in the input sequence.
    """
    seen = set()
    for item in seq:
        if item not in seen:
            seen.add(item)
            yield item

def prefix_length(a: str, b: str) -> int:
    """
    Searches for the length of overlap in the starting
    characters of string b in a. Uses binary search
    if b is not already a prefix of a.
    """
    if a.startswith(b):
        return len(b)
    left, right = 0, min(len(a), len(b))
    while left < right:
        mid = (left + right + 1) // 2
        if a.startswith(b[:mid]):
            left = mid
        else:
            right = mid - 1
    return left


def camel_to_kebab(name):
    # Use regular expressions to insert a hyphen before each uppercase letter not at the start,
    # and between a lowercase and uppercase letter.
    kebab_case = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', name)
    kebab_case = re.sub(r'([A-Z]+)([A-Z][a-z0-9])', r'\1-\2', kebab_case)
    return kebab_case.lower()
