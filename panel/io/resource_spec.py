"""
Derives the client-side resource specification for component classes.

The specification is the payload the browser needs in order to load a
component's external libraries on demand. It is derived entirely from the
declarations components already make (``__javascript_raw__``,
``__javascript_modules_raw__``, ``__javascript_module_exports__``,
``__css_raw__`` and ``__js_skip__``), so third-party component authors get
lazy loading without any new API.

The same specification feeds both delivery paths:

* the lazy path, where it is carried by the ``external_resources`` property
  of a model instance and resolved by the client-side registry, and
* the eager path, where ``pn.extension`` renders the script and link tags
  into the page and the templates call ``declare()`` on the registry with
  the specs it just satisfied.

Generating both from one function is what keeps them from drifting.
"""
from __future__ import annotations

import copy
import pathlib
import re
import typing as t

from bokeh.model import Model

from ..config import config
from ..util import isurl
from .resources import (
    Resources, component_resource_path, extension_declared, get_resource_mode,
    resolve_resource_cdn, set_resource_mode,
)
from .state import state

if t.TYPE_CHECKING:
    from .resources import MODES

# Version of the specification format. The client-side registry is shared
# across Panel versions on a single page, so this has to be bumped in
# lockstep with any backwards incompatible change to the payload shape.
SPEC_VERSION = 1

# Attributes whose presence anywhere in the MRO means a class may declare
# resources. Checked against ``__dict__`` so that ``classproperty``
# declarations are not evaluated, which is what makes the common case (a
# model with no resources at all) cheap.
_RESOURCE_ATTRS = (
    '__javascript_raw__',
    '__javascript__',
    '__javascript_modules_raw__',
    '__javascript_modules__',
    '__css_raw__',
    '__css__',
)

_CUSTOM_ELEMENT_RE = re.compile(r"^customElements\.get\(\s*['\"]([^'\"]+)['\"]\s*\)\s*$")

_SPEC_CACHE: dict[t.Any, dict[str, t.Any] | None] = {}


class _Entry(t.NamedTuple):
    kind: t.Literal['js', 'module']
    raw: str
    url: str
    export: str | None


def _spec_mode(mode: MODES | None = None) -> tuple[str, bool]:
    """
    Resolves the mode urls should be generated for.

    ``inline`` has no urls to hand out, so it falls back to the CDN form
    and flags the specification, which the loader reports at debug level.
    """
    resolved = mode or get_resource_mode()
    if resolved == 'inline':
        return 'cdn', True
    return resolved, False


def _resources(mode: str) -> Resources:
    return Resources(mode=mode)


def _parse_probe(expression: str) -> dict[str, str] | None:
    """
    Converts a ``__js_skip__`` key into a structured probe.

    ``__js_skip__`` keys are JavaScript expressions today, e.g.
    ``Perspective`` uses ``customElements.get('perspective-viewer')``.
    Structuring them means nothing has to be evaluated client-side, which
    keeps strict CSP deployments (no ``unsafe-eval``) working.
    """
    expression = expression.strip()
    match = _CUSTOM_ELEMENT_RE.match(expression)
    if match:
        return {'custom_element': match.group(1)}
    if expression.isidentifier():
        return {'global': expression}
    return None


def _js_skip(cls: type) -> dict[str, list[str]]:
    """
    Reads ``__js_skip__``, tolerating the broken declarations out there.
    """
    try:
        skip = getattr(cls, '__js_skip__', None) or {}
    except Exception:
        return {}
    if not isinstance(skip, dict):
        return {}
    resolved = {}
    for key, urls in skip.items():
        if isinstance(urls, str):
            urls = [urls]
        elif not isinstance(urls, (list, tuple)):
            continue
        resolved[key] = [url for url in urls if isinstance(url, str)]
    return resolved


def _bokeh_pairs(
    cls: type, attr: str, resources: Resources
) -> list[tuple[str, str]]:
    """
    Pairs a Bokeh model class' declared urls with their resolved form.

    The declared (``bundled_files``) form is what ``__js_skip__`` refers
    to, the resolved (``adjust_paths``) form is what the browser fetches,
    so grouping needs both.
    """
    try:
        raw = getattr(cls, attr, None) or []
    except Exception:
        return []
    raw = [url for url in raw if isinstance(url, str)]
    return list(zip(raw, resources.adjust_paths(raw)))


def _panel_pairs(
    cls: type, attr: str, resources: Resources
) -> list[tuple[str, str]]:
    """
    Same as ``_bokeh_pairs`` for ``ReactiveHTML``/``ReactiveESM`` classes.

    Their resources are declared on the Panel class rather than the shared
    Bokeh model, and are resolved the way ``Resources.extra_resources``
    resolves them, i.e. relative paths become component resource urls.
    """
    try:
        declared = getattr(cls, attr, None) or []
    except Exception:
        return []

    # extra_resources attributes the resources to the class that declared
    # them, so that component resource urls point at the right module.
    owner = cls
    for supcls in cls.__mro__[1:]:
        if getattr(supcls, attr, None) == declared:
            owner = supcls

    raw, resolved = [], []
    for resource in declared:
        if isinstance(resource, pathlib.PurePath) or not isinstance(resource, str):
            continue
        url = resource
        if resources.mode == 'cdn':
            url = str(resolve_resource_cdn(url))
        if state.rel_path:
            url = url.removeprefix(state.rel_path+'/')
        if not isurl(url) and not url.lstrip('./').startswith('static/extensions'):
            url = component_resource_path(owner, attr, url)
        raw.append(resource)
        resolved.append(url)
    return list(zip(raw, resources.adjust_paths(resolved)))


def _declaring_owner(cls: type) -> type:
    """
    The class in the MRO that declared the resources, most derived first.

    Naming anonymous groups after it rather than after ``cls`` is what makes
    the three ESM models (which all inherit es-module-shims from
    ``ReactiveESM``) share one group instead of declaring three.
    """
    for supcls in getattr(cls, '__mro__', (cls,)):
        if any(attr in supcls.__dict__ for attr in _RESOURCE_ATTRS):
            return supcls
    return cls


def _build_libs(cls: type, entries: list[_Entry], skip: dict[str, list[str]]) -> list[dict]:
    """
    Groups a class' urls into libraries, one per global they provide.

    ``__js_skip__`` maps a global name to the subset of urls providing it,
    which is exactly the grouping wanted. Urls no global claims become one
    anonymous group loaded in declared order (deck.gl's loaders, filepond's
    plugins, echarts-gl).
    """
    index_of: dict[str, int] = {}
    for i, entry in enumerate(entries):
        index_of.setdefault(entry.raw, i)

    probes: dict[str, dict[str, str]] = {}
    order: dict[str, int] = {}
    group_of: dict[str, str] = {}
    for expression, urls in skip.items():
        probe = _parse_probe(expression)
        if probe is None:
            continue
        indices = [index_of[url] for url in urls if url in index_of]
        if not indices:
            continue
        name = probe.get('global') or probe['custom_element']
        probes[name] = probe
        order[name] = min(order.get(name, len(entries)), min(indices))
        for url in urls:
            if url in index_of:
                group_of.setdefault(url, name)

    anonymous = f'{_declaring_owner(cls).__name__.lower()}:extra'
    for i, entry in enumerate(entries):
        if entry.raw not in group_of:
            group_of[entry.raw] = anonymous
            order.setdefault(anonymous, i)

    libs: dict[str, dict[str, t.Any]] = {}
    for entry in entries:
        name = group_of[entry.raw]
        lib = libs.setdefault(name, {'name': name})
        if entry.kind == 'js':
            lib.setdefault('js', []).append(entry.url)
        else:
            module: dict[str, str] = {'url': entry.url}
            if entry.export:
                module['export'] = entry.export
            lib.setdefault('modules', []).append(module)
    for name, probe in probes.items():
        if name in libs:
            libs[name]['probe'] = probe

    return [libs[name] for name in sorted(libs, key=lambda name: order[name])]


def _shim_url(resources: Resources) -> str | None:
    """
    The es-module-shims url, needed before any module can be imported.

    Today the shim only reaches the page if ``ReactiveESM.__javascript__``
    happened to be collected, so a notebook that never used an ESM
    component has no ``importShim`` at all. Carrying it on any spec that
    contains modules closes that gap.
    """
    from ..models.esm import ReactiveESM
    urls = resources.adjust_paths(ReactiveESM.__javascript__)
    return urls[0] if urls else None


def _has_resources(cls: type) -> bool:
    mro = getattr(cls, '__mro__', (cls,))
    return any(
        attr in supcls.__dict__
        for attr in _RESOURCE_ATTRS
        for supcls in mro
    )


def _build_spec(cls: type, mode: str) -> dict[str, t.Any] | None:
    from ..reactive import ReactiveCustomBase

    with set_resource_mode(mode):  # type: ignore[arg-type]
        resources = _resources(mode)
        pairs = _panel_pairs if issubclass(cls, ReactiveCustomBase) else _bokeh_pairs
        js = pairs(cls, '__javascript__', resources)
        modules = pairs(cls, '__javascript_modules__', resources)
        css = [url for _, url in pairs(cls, '__css__', resources)]
        try:
            exports = list(getattr(cls, '__javascript_module_exports__', None) or [])
        except Exception:
            exports = []
        skip = _js_skip(cls)

        entries = [_Entry('js', raw, url, None) for raw, url in js]
        entries += [
            _Entry('module', raw, url, exports[i] if i < len(exports) else None)
            for i, (raw, url) in enumerate(modules)
        ]

        if not entries and not css:
            return None

        spec: dict[str, t.Any] = {'v': SPEC_VERSION}
        if entries:
            spec['libs'] = _build_libs(cls, entries, skip)
        if css:
            spec['css'] = css
        if modules:
            shim = _shim_url(resources)
            if shim:
                spec['shim'] = shim
        return spec


def resource_spec(cls: type, mode: MODES | None = None) -> dict[str, t.Any] | None:
    """
    Builds the client-side resource specification for a component class.

    Groups the class' ``__javascript__`` urls by the global they provide
    (from ``__js_skip__``), resolves them for the active resource mode via
    the same ``bundled_files``/``adjust_paths`` machinery the eager path
    uses, and appends ``__javascript_modules__`` (with their
    ``__javascript_module_exports__`` names) and ``__css__``.

    Parameters
    ----------
    cls: type
        A Bokeh model class, or a ``ReactiveHTML``/``ReactiveESM``
        subclass, whose resources are declared on the Panel class.
    mode: MODES | None
        Resource mode to resolve urls for, defaulting to the active one.

    Returns
    -------
    The specification, or None if the class declares no resources or lazy
    loading is disabled.
    """
    if not config.lazy_resources or not _has_resources(cls):
        return None
    resolved_mode, inline_fallback = _spec_mode(mode)
    key = (
        cls, resolved_mode, state.rel_path, state.base_url,
        tuple(getattr(cls, '__css_raw__', None) or ()),
    )
    if key in _SPEC_CACHE:
        spec = _SPEC_CACHE[key]
    else:
        spec = _SPEC_CACHE[key] = _build_spec(cls, resolved_mode)
    if spec is None:
        return None
    spec = copy.deepcopy(spec)
    spec['timeout'] = config.resource_timeout
    if inline_fallback:
        spec['inline_fallback'] = True
    return spec


def lazy_load_available(notebook: bool = False) -> bool:
    """
    Whether a component that was not declared can still get its resources.

    False when lazy loading was switched off, and for self-contained
    ``inline`` output, where there is nothing left to inline after the fact
    and the component would silently fall back to the CDN. Notebooks are
    exempt from the latter: their output is never self-contained anyway.
    """
    if not config.lazy_resources:
        return False
    return notebook or get_resource_mode() != 'inline'


def _resource_classes() -> list[type]:
    """
    The classes whose resources the eager path has put on the page.

    Mirrors ``Resources._collect_external_resources`` and
    ``Resources.extra_resources``, extension gate included, so that what
    is declared to the registry is exactly what was rendered.
    """
    from ..reactive import ReactiveCustomBase
    from ..util import _descendents

    classes = [
        cls for _, cls in sorted(Model.model_class_reverse_map.items(), key=lambda item: item[0])
        if extension_declared(cls)
    ]
    classes += [
        cls for cls in _descendents(ReactiveCustomBase, concrete=True) if cls._loaded()
    ]
    return classes


def declared_specs(mode: MODES | None = None) -> dict[str, t.Any]:
    """
    The resources the eager path has already satisfied.

    Rendered into the page (and the notebook bootstrap) as a ``declare()``
    call so that the registry knows about them without having to infer it
    from the DOM, which is the only thing that works in ``inline`` mode,
    where the libraries were inlined and have no urls at all.
    """
    if not config.lazy_resources:
        return {}
    resolved_mode, _ = _spec_mode(mode)
    libs: dict[str, dict[str, t.Any]] = {}
    css: list[str] = []
    for cls in _resource_classes():
        if not _has_resources(cls):
            continue
        try:
            spec = _build_spec(cls, resolved_mode)
        except Exception:
            continue
        if spec is None:
            continue
        for lib in spec.get('libs', []):
            libs.setdefault(lib['name'], lib)
        for url in spec.get('css', []):
            if url not in css:
                css.append(url)
    if not libs and not css:
        return {}
    declared: dict[str, t.Any] = {}
    if libs:
        declared['libs'] = list(libs.values())
    if css:
        declared['css'] = css
    return copy.deepcopy(declared)
