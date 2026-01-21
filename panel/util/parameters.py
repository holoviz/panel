from __future__ import annotations

import inspect

from collections import defaultdict
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, cast

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
def edit_readonly(parameterized: param.Parameterized) -> Iterator[None]:
    """
    Temporarily set parameters on Parameterized object to readonly=False
    to allow editing them.
    """
    kls_params = parameterized.param.objects(instance=False)
    inst_params = cast(dict[str, param.Parameter], parameterized._param__private.params)
    init_inst_params = list(inst_params)
    updated: dict[str, list[str]] = defaultdict(list)
    for pname, pobj in (kls_params | inst_params).items():
        if pobj.readonly:
            if not pobj.constant:
                # The Parameter constructor sets constant to True if readonly
                # is True. This is to support the rare case where a user
                # would later on update constant to be False while keeping
                # readonly True.
                updated['readonly_not_constant'].append(pname)
            else:
                updated['readonly'].append(pname)
            pobj.readonly = False
            pobj.constant = False
        elif pobj.constant:
            updated['constant'].append(pname)
            pobj.constant = False
    try:
        yield
    finally:
        # Some operations trigger a parameter instantiation (copy),
        # for these three cases we ensure both the class and instance parameters
        # are reset.
        for pname in updated['readonly_not_constant']:
            if pname in kls_params and pname not in init_inst_params:
                type(parameterized).param[pname].readonly = True
            if pname in inst_params:
                parameterized.param[pname].readonly = True
        for pname in updated['readonly']:
            if pname in kls_params and pname not in init_inst_params:
                type(parameterized).param[pname].readonly = True
                type(parameterized).param[pname].constant = True
            if pname in inst_params:
                parameterized.param[pname].readonly = True
                parameterized.param[pname].constant = True
        for pname in updated['constant']:
            if pname in kls_params and pname not in init_inst_params:
                type(parameterized).param[pname].constant = True
            if pname in inst_params:
                parameterized.param[pname].constant = True


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
                    raise ValueError(f'Cannot depend on undefined sub-parameter {p!r}.')
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
