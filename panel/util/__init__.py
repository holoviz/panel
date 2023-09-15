"""
Various general utilities used in the panel codebase.
"""
from __future__ import annotations

import ast
import base64
import datetime as dt
import inspect
import json
import numbers
import os
import pathlib
import re
import sys
import urllib.parse as urlparse

from collections import OrderedDict, defaultdict
from collections.abc import MutableMapping, MutableSequence
from contextlib import contextmanager
from datetime import datetime
from functools import partial
from html import escape  # noqa
from importlib import import_module
from typing import Any, AnyStr, Iterator

import bleach
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

bokeh_version = Version(bokeh.__version__)

# Bokeh serializes NaT as this value
# Discussion on why https://github.com/bokeh/bokeh/pull/10449/files#r479988469
BOKEH_JS_NAT = -9223372036854776.0

PARAM_NAME_PATTERN = re.compile(r'^.*\d{5}$')

HTML_SANITIZER = bleach.sanitizer.Cleaner(strip=True)


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
    raise ValueError('%s not in list' % obj)


def param_name(name: str) -> str:
    """
    Removes the integer id from a Parameterized class name.
    """
    match = re.findall(r'\D+(\d{5,})', name)
    return name[:name.index(match[0])] if match else name


def recursive_parameterized(parameterized: param.Parameterized, objects=None) -> list[param.Parameterized]:
    """
    Recursively searches a Parameterized object for other Parmeterized
    objects.
    """
    objects = [] if objects is None else objects
    objects.append(parameterized)
    for p in parameterized.param.values().values():
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


def get_method_owner(meth):
    """
    Returns the instance owning the supplied instancemethod or
    the class owning the supplied classmethod.
    """
    if inspect.ismethod(meth):
        return meth.__self__


def extract_dependencies(function):
    """
    Extract references from a method or function that declares the references.
    """
    subparameters = list(function._dinfo['dependencies'])+list(function._dinfo['kw'].values())
    params = []
    for p in subparameters:
        if isinstance(p, str):
            owner = get_method_owner(function)
            *subps, p = p.split('.')
            for subp in subps:
                owner = getattr(owner, subp, None)
                if owner is None:
                    raise ValueError('Cannot depend on undefined sub-parameter {p!r}.')
            if p in owner.param:
                pobj = owner.param[p]
                if pobj not in params:
                    params.append(pobj)
            else:
                for sp in extract_dependencies(getattr(owner, p)):
                    if sp not in params:
                        params.append(sp)
        elif p not in params:
            params.append(p)
    return params


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
        elif v.startswith('[') or v.startswith('{'):
            try:
                parsed_query[k] = json.loads(v)
            except Exception:
                parsed_query[k] = ast.literal_eval(v)
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


# This functionality should be contributed to param
# See https://github.com/holoviz/param/issues/379
@contextmanager
def edit_readonly(parameterized: param.Parameterized) -> Iterator:
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


def eval_function(function):
    args, kwargs = (), {}
    if hasattr(function, '_dinfo'):
        arg_deps = function._dinfo['dependencies']
        kw_deps = function._dinfo.get('kw', {})
        if kw_deps or any(isinstance(d, param.Parameter) for d in arg_deps):
            args = (getattr(dep.owner, dep.name) for dep in arg_deps)
            kwargs = {n: getattr(dep.owner, dep.name) for n, dep in kw_deps.items()}
    return function(*args, **kwargs)


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


def fullpath(path: AnyStr | os.PathLike) -> AnyStr | os.PathLike:
    """Expanduser and then abspath for a given path
    """
    return os.path.abspath(os.path.expanduser(path))


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

_unset = object()

def param_watchers(parameterized, value=_unset):
    if Version(param.__version__) <= Version('2.0.0a2'):
        if value is not _unset:
            parameterized._param_watchers = value
        else:
            return parameterized._param_watchers
    else:
        if value is not _unset:
            parameterized.param.watchers = value
        else:
            return parameterized.param.watchers
