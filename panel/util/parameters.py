from __future__ import annotations

import inspect

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import param


def should_inherit(parameterized: param.Parameterized, p: str, v: Any) -> Any:
    pobj = parameterized.param[p]
    return v is not pobj.default and not pobj.readonly and (v is not None or pobj.allow_None)


def get_params_to_inherit(parameterized: param.Parameterized) -> dict:
    return {
        p: v for p, v in parameterized.param.values().items()
        if should_inherit(parameterized, p, v)
    }


def get_method_owner(meth):
    """
    Returns the instance owning the supplied instancemethod or
    the class owning the supplied classmethod.
    """
    if inspect.ismethod(meth):
        return meth.__self__


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
