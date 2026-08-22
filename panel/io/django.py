"""
Native Django integration for Panel applications.

Panel applications are served by :class:`panel.io.asgi.PanelASGI`, which is
composed with Django's own ASGI application. The routes Panel owns, i.e. the
application documents, ``/autoload.js``, the websocket, BokehJS and component
resources, are dispatched to Panel and everything else is handed to Django.

This replaces the ``bokeh-django``/Channels based integration, which is no
longer needed. The ``document``, ``autoload``, ``directory``,
``static_extensions``, ``with_request`` and ``with_url_args`` helpers are kept
so that an existing project only has to replace its Channels routing with
:func:`panel.io.django.get_asgi_application`.
"""
from __future__ import annotations

import asyncio
import inspect
import logging
import os
import re
import typing as t

from pathlib import Path

from bokeh.application.application import Application as BkApplication
from bokeh.application.handlers.document_lifecycle import (
    DocumentLifecycleHandler,
)
from bokeh.command.util import build_single_handler_applications
from bokeh.embed.bundle import extension_dirs
from bokeh.settings import settings as bokeh_settings

from .application import Application, build_single_handler_application
from .asgi import PanelASGI
from .auth import configure_auth, pop_auth_kwargs
from .handlers import FunctionHandler
from .state import set_curdoc, state

try:
    from django.contrib.staticfiles.finders import BaseFinder
except ImportError:
    msg = 'django must be installed to use the panel.io.django module.'
    raise ImportError(msg) from None

if t.TYPE_CHECKING:
    from collections.abc import (
        Callable, Iterable, Mapping, Sequence,
    )

    from bokeh.document import Document
    from bokeh.server.contexts import ApplicationContext

    from .asgi import Receive, Scope, Send

    ApplicationLike: t.TypeAlias = BkApplication | Callable[[Document], t.Any] | os.PathLike | str

logger = logging.getLogger(__name__)

__all__ = (
    "PanelDjangoASGI",
    "PanelExtensionFinder",
    "Routing",
    "autoload",
    "directory",
    "document",
    "get_asgi_application",
    "static_extensions",
    "with_request",
    "with_url_args",
)

# Routes Panel serves as a convenience but which Django should win, so that
# adding Panel apps to a project does not take over its root URLs.
DEFERRED_ROUTES = ('/', '/favicon.ico')

_NAMED_GROUP = re.compile(r'\(\?P<(?P<name>\w+)>[^)]*\)')


#---------------------------------------------------------------------
# Routing
#---------------------------------------------------------------------

def _normalize_url(url: str) -> str:
    """
    Normalizes a Django style URL into an application path, i.e. strips
    the regex anchors and slashes ``bokeh-django`` allowed and translates
    named regex groups into Panel's ``{param}`` route templates.
    """
    url = url.strip().strip('^$')
    if _NAMED_GROUP.search(url):
        converted = _NAMED_GROUP.sub(lambda m: f"{{{m.group('name')}}}", url)
        logger.warning(
            "Converted regex route %r to the route template %r. Declare "
            "routes with parameters as '{name}' templates instead.",
            url, converted
        )
        url = converted
    url = url.strip('/')
    return f'/{url}' if url else '/'


def _run_coroutine_handler(func: Callable[[Document], t.Any]) -> Callable[[Document], None]:
    """
    Adapts a coroutine application function to the synchronous
    ``modify_document`` API.

    Function based applications are initialized on a worker thread (see
    ``ApplicationContext._initialize_document_async``), so the coroutine is
    scheduled on the server event loop and awaited from there.
    """
    def wrapper(doc: Document) -> None:
        loop: asyncio.AbstractEventLoop | None
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            io_loop = state._document_loop(doc)
            loop = t.cast(
                'asyncio.AbstractEventLoop | None',
                getattr(io_loop, 'asyncio_loop', io_loop)
            )
        else:
            # Already on the event loop, so we cannot block on the coroutine.
            loop = None
        if loop is None:
            raise RuntimeError(
                f"Could not run the coroutine application function {func!r} "
                "because it was initialized on the event loop thread. Declare "
                "the application function with 'def' and schedule any "
                "asynchronous work with pn.state.onload instead."
            )

        async def run() -> None:
            with set_curdoc(doc):
                await func(doc)

        asyncio.run_coroutine_threadsafe(run(), loop).result()

    return wrapper


class Routing:
    """
    Declares a Panel application served on a URL.

    Parameters
    ----------
    url: str
        The URL to serve the application on.
    app: Application, callable or path
        The application to serve, either a Bokeh/Panel ``Application``, a
        function that modifies a Document or the path to an application
        script, notebook or directory.
    document: bool
        Whether to serve the rendered application on the URL itself.
    autoload: bool
        Whether to serve the application for embedding in a Django view,
        i.e. on ``<url>/autoload.js``.
    """

    url: str
    app: BkApplication
    document: bool
    autoload: bool

    def __init__(
        self, url: str, app: ApplicationLike, *, document: bool = False,
        autoload: bool = False
    ) -> None:
        self.url = _normalize_url(url)
        self.app = self._fixup(self._normalize(app))
        self.document = document
        self.autoload = autoload

    def __repr__(self) -> str:
        kind = 'document' if self.document else 'autoload'
        return f'<{self.__module__}.{type(self).__name__} url="{self.url}" {kind}>'

    def _normalize(self, obj: ApplicationLike) -> BkApplication:
        if isinstance(obj, BkApplication):
            return obj
        elif isinstance(obj, (str, os.PathLike)):
            return build_single_handler_application(obj)
        elif callable(obj):
            func = _run_coroutine_handler(obj) if inspect.iscoroutinefunction(obj) else obj
            return Application(FunctionHandler(func, trap_exceptions=True))
        raise ValueError(
            f"Could not serve {obj!r} as a Panel application. Supply an "
            "Application, a function that modifies a Document or the path "
            "to an application script, notebook or directory."
        )

    def _fixup(self, app: BkApplication) -> BkApplication:
        if not any(isinstance(handler, DocumentLifecycleHandler) for handler in app.handlers):
            app.add(DocumentLifecycleHandler())
        return app


def document(url: str, app: ApplicationLike) -> Routing:
    """
    Declares an application to serve as a full page on the given URL.
    """
    return Routing(url, app, document=True)


def autoload(url: str, app: ApplicationLike) -> Routing:
    """
    Declares an application to embed in a Django view, i.e. it is served
    on ``<url>/autoload.js`` and rendered by the script the
    ``bokeh.embed.server_document`` helper generates.
    """
    return Routing(url, app, autoload=True)


def directory(*apps_paths: str | os.PathLike) -> list[Routing]:
    """
    Declares all applications in one or more directories, serving each of
    them as a full page on the URL matching its filename.
    """
    paths: list[str] = []
    for apps_path in apps_paths:
        path = Path(apps_path)
        if path.exists():
            paths += [str(entry) for entry in path.glob('*') if _is_panel_app(entry)]
        else:
            logger.warning("Panel applications directory %r doesn't exist", str(path))
    return [document(url, app) for url, app in build_single_handler_applications(paths).items()]


def _is_panel_app(entry: Path) -> bool:
    return (
        (entry.is_dir() or entry.name.endswith(('.py', '.ipynb', '.md'))) and
        not entry.name.startswith(('.', '_'))
    )


#---------------------------------------------------------------------
# Application helpers
#---------------------------------------------------------------------

def with_request(handler):
    """
    Wraps an application function so that it is called with the HTTP
    request that created the session in addition to the Document.
    """
    # functools.wraps cannot be used here because Bokeh requires that the
    # signature of the returned function accepts a single (Document) argument
    def wrapper(doc):
        return handler(doc, doc.session_context.request)

    async def async_wrapper(doc):
        return await handler(doc, doc.session_context.request)

    return async_wrapper if inspect.iscoroutinefunction(handler) else wrapper


def _get_args_kwargs_from_doc(doc) -> tuple[tuple[t.Any, ...], dict[str, t.Any]]:
    request = doc.session_context.request
    url_route = getattr(request, 'url_route', None)
    if url_route:
        return tuple(url_route['args']), dict(url_route['kwargs'])
    with set_curdoc(doc):
        return (), dict(state.route_params)


def with_url_args(handler):
    """
    Wraps an application function so that it is called with the parameters
    captured by the route it is served on, e.g. an application declared on
    ``/user/{name}`` is called with the ``name`` keyword argument.
    """
    # functools.wraps cannot be used here because Bokeh requires that the
    # signature of the returned function accepts a single (Document) argument
    def wrapper(doc):
        args, kwargs = _get_args_kwargs_from_doc(doc)
        return handler(doc, *args, **kwargs)

    async def async_wrapper(doc):
        args, kwargs = _get_args_kwargs_from_doc(doc)
        return await handler(doc, *args, **kwargs)

    return async_wrapper if inspect.iscoroutinefunction(handler) else wrapper


#---------------------------------------------------------------------
# Static file handling
#---------------------------------------------------------------------

def _resolve_static(root: str | os.PathLike | None, relative: str) -> Path | None:
    if root is None or not relative:
        return None
    root_path = Path(root).resolve()
    path = (root_path / relative).resolve()
    if not path.is_relative_to(root_path) or not path.is_file():
        return None
    return path


def _resolve_bokeh_static(route: str) -> Path | None:
    """
    Resolves a ``/static/`` URL against the directories Bokeh and Panel
    serve their own resources from, i.e. BokehJS and the extension
    directories. Returns None if the route does not refer to one of them,
    in which case Django serves it.
    """
    relative = route.removeprefix('/static/')
    if relative.startswith('extensions/'):
        name, separator, artifact = relative.removeprefix('extensions/').partition('/')
        if not separator:
            return None
        return _resolve_static(extension_dirs.get(name), artifact)
    return _resolve_static(bokeh_settings.bokehjs_path(), relative)


class PanelExtensionFinder(BaseFinder):
    """
    A staticfiles finder which serves the resources of Panel and Bokeh
    extensions.

    Only needed if the Django development server is used to serve the
    static files, e.g. because the applications are embedded in Django
    views with ``autoload``. Add it to the ``STATICFILES_FINDERS`` in the
    Django settings:

        STATICFILES_FINDERS = [
            'django.contrib.staticfiles.finders.FileSystemFinder',
            'django.contrib.staticfiles.finders.AppDirectoriesFinder',
            'panel.io.django.PanelExtensionFinder',
        ]
    """

    _root = extension_dirs
    _prefix = 'extensions/'

    def __init__(self, app_names=None, *args, **kwargs):
        pass

    def check(self, **kwargs):
        return []

    def find(self, path, find_all=False, **kwargs):
        """
        Given a relative file path, find an absolute file path.

        If the ``find_all`` parameter is False (default) return only the
        first found file path; if True, return a list of all found file
        paths.
        """
        # Django <5.2 passes the flag as 'all'
        find_all = find_all or kwargs.get('all', False)
        location = self.find_location(path, self._prefix)
        if location is None:
            return []
        return [location] if find_all else location

    def list(self, ignore_patterns):
        """
        Lists all the extension resources, so that they are collected by
        the ``collectstatic`` management command.
        """
        from django.core.files.storage import FileSystemStorage
        for name, artifacts_dir in self._root.items():
            root = Path(artifacts_dir)
            if not root.is_dir():
                continue
            storage = FileSystemStorage(location=root)
            storage.prefix = f'{self._prefix}{name}'
            for artifact in root.rglob('*'):
                if artifact.is_file():
                    yield str(artifact.relative_to(root)), storage

    @classmethod
    def find_location(cls, path, prefix=None, as_components=False):
        """
        Find the absolute path of a resource given a relative path.

        Args:
            path (str): relative path to the resource
            prefix (str): if given, verifies that path starts with `prefix`
                else returns `None`
            as_components (bool): If `True` return a tuple of
                (artifacts_dir, artifact_path) rather than the absolute
                path. Used when the components have to be passed to
                Django's `static.serve` view separately.
        """
        prefix = prefix or ''
        if prefix and not path.startswith(prefix):
            return None
        path = path[len(prefix):]
        name, separator, artifact_path = path.replace(os.sep, '/').partition('/')
        if not separator:
            return None
        artifacts_dir = cls._root.get(name)
        resolved = _resolve_static(artifacts_dir, artifact_path)
        if resolved is None:
            return None
        elif as_components:
            return artifacts_dir, artifact_path
        return str(resolved)


# Kept for compatibility with bokeh_django.static
BokehExtensionFinder = PanelExtensionFinder


def serve_extensions(request, path):
    from django.http import Http404
    from django.views import static
    components = PanelExtensionFinder.find_location(path, as_components=True)
    if components is None:
        raise Http404
    artifacts_dir, artifact_path = components
    return static.serve(request, artifact_path, document_root=artifacts_dir)


def static_extensions(prefix: str = "/static/extensions/"):
    """
    Returns the urlpatterns serving the resources of Panel and Bokeh
    extensions from Django.

    Only needed if the applications are embedded in Django views with
    ``autoload`` and Django serves the static files.
    """
    from django.urls import re_path
    escaped = re.escape(prefix.lstrip('/'))
    return [re_path(rf'^{escaped}(?P<path>.*)$', serve_extensions)]


#---------------------------------------------------------------------
# ASGI application
#---------------------------------------------------------------------

class PanelDjangoASGI(PanelASGI):
    """
    An ASGI3 application serving Panel application(s) alongside a Django
    application.

    Requests for the routes Panel owns, i.e. the applications and their
    websocket, autoload and resource endpoints, are served by Panel; every
    other request is handed to the Django application.

    Parameters
    ----------
    applications: Mapping[str, Application]
        The application(s) to serve.
    django_app: ASGI application
        The application to hand all other requests to. Defaults to
        ``django.core.asgi.get_asgi_application()``.
    document_paths: Iterable[str] | None
        The application paths that serve their rendered document. Paths
        that are not listed are only served for embedding, i.e. Django
        renders the page on the application path itself. Defaults to all
        applications.
    kwargs: dict
        Additional keyword arguments to pass to ``PanelASGI``.
    """

    def __init__(
        self,
        applications: Mapping[str, BkApplication],
        *,
        django_app: t.Any = None,
        document_paths: Iterable[str] | None = None,
        **kwargs
    ) -> None:
        # Django owns the root URL and the index it may serve there
        kwargs.setdefault('index_enabled', False)
        super().__init__(applications, **kwargs)
        if django_app is None:
            from django.core.asgi import get_asgi_application
            django_app = get_asgi_application()
        self._django_app = django_app
        self._document_paths = (
            None if document_paths is None else
            {_normalize_url(url) for url in document_paths}
        )

    @property
    def django_app(self) -> t.Any:
        return self._django_app

    def _resolve_route(
        self, route: str
    ) -> tuple[ApplicationContext, str, dict[str, str]] | None:
        resolved = super()._resolve_route(route)
        if resolved is None:
            return None
        context, suffix, _ = resolved
        if (
            suffix in ('', '/') and self._document_paths is not None
            and context.url not in self._document_paths
        ):
            # The application is only served for embedding, so Django
            # renders the page on the application path itself.
            return None
        return resolved

    def _django_resolves(self, route: str) -> bool:
        from django.urls import resolve
        try:
            resolve(route)
        except Exception:
            return False
        return True

    def handles(self, scope: Scope) -> bool:
        if scope['type'] not in ('http', 'websocket'):
            return False
        route = self._route_path(scope)
        if not route:
            return False
        if route.startswith('/static/'):
            root_context = self._core.applications.get('/')
            if root_context is not None and root_context.application.static_path:
                return True
            return _resolve_bokeh_static(route) is not None
        if self._resolve_route(route) is not None:
            return True
        if route in DEFERRED_ROUTES:
            return not self._django_resolves(route) and super().handles(scope)
        return any(pattern.match(route) for pattern, _ in self._extra_routes)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] == 'lifespan':
            # Django's ASGI handler does not implement the lifespan protocol
            await self._lifespan(receive, send)
            return
        elif self.handles(scope):
            await super().__call__(scope, receive, send)
            return
        elif scope['type'] == 'websocket' and self._django_rejects_websockets():
            await receive()
            await send({'type': 'websocket.close', 'code': 1000})
            return
        await self._django_app(scope, receive, send)

    def _django_rejects_websockets(self) -> bool:
        from django.core.handlers.asgi import ASGIHandler
        return isinstance(self._django_app, ASGIHandler)


def get_asgi_application(
    routings: Routing | Sequence[Routing | Sequence[Routing]],
    *,
    django_app: t.Any = None,
    **kwargs
) -> PanelDjangoASGI:
    """
    Builds the ASGI application serving the declared Panel application(s)
    alongside a Django application.

    Declare it as the ASGI application of the project, e.g. in
    ``project/asgi.py``:

        import os

        from panel.io.django import document, get_asgi_application

        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

        import my_app.pn_app as pn_app

        application = get_asgi_application([document('sliders', pn_app.app)])

    and serve it with an ASGI server, e.g.
    ``uvicorn project.asgi:application``.

    Parameters
    ----------
    routings: Routing | list[Routing]
        The application(s) to serve, declared with ``document``,
        ``autoload`` or ``directory``.
    django_app: ASGI application
        The application to hand all non-Panel requests to. Defaults to
        ``django.core.asgi.get_asgi_application()``.
    kwargs: dict
        Additional keyword arguments to pass to the ``PanelASGI``
        application, including the authentication arguments applied by
        ``panel.io.auth.configure_auth``, e.g. ``basic_auth`` or
        ``oauth_provider``.

    Returns
    -------
    The ASGI application.
    """
    if isinstance(routings, Routing):
        routings = [routings]
    flattened: list[Routing] = []
    for routing in routings:
        if isinstance(routing, Routing):
            flattened.append(routing)
        elif isinstance(routing, (list, tuple)):
            flattened.extend(routing)
        else:
            raise ValueError(
                f"Could not serve {routing!r}, declare applications with the "
                "panel.io.django.document, autoload and directory helpers."
            )

    applications: dict[str, BkApplication] = {}
    document_paths: set[str] = set()
    for routing in flattened:
        if not isinstance(routing, Routing):
            raise ValueError(
                f"Could not serve {routing!r}, declare applications with the "
                "panel.io.django.document, autoload and directory helpers."
            )
        elif routing.url in applications:
            raise ValueError(
                f"Multiple applications declared on the URL {routing.url!r}."
            )
        applications[routing.url] = routing.app
        if routing.document:
            document_paths.add(routing.url)

    if websocket_origin := kwargs.pop('websocket_origin', None):
        if not isinstance(websocket_origin, list):
            websocket_origin = [websocket_origin]
        kwargs['extra_websocket_origins'] = websocket_origin

    auth_provider, server_config = configure_auth(**pop_auth_kwargs(kwargs))
    return PanelDjangoASGI(
        applications, django_app=django_app, document_paths=document_paths,
        auth_provider=auth_provider, server_config=server_config, **kwargs
    )


#---------------------------------------------------------------------
# Removed bokeh-django API
#---------------------------------------------------------------------

_CHANNELS_REMOVED = (
    "{name} is no longer available. Panel serves Django applications on its "
    "own ASGI application, so channels and bokeh-django are not needed "
    "anymore. Declare the applications with panel.io.django.document or "
    "panel.io.django.autoload and serve them with "
    "panel.io.django.get_asgi_application(routings). See "
    "https://panel.holoviz.org/how_to/integrations/Django.html"
)


def _removed(name: str):
    def raise_removed(*args, **kwargs):
        raise RuntimeError(_CHANNELS_REMOVED.format(name=name))
    return raise_removed


class RoutingConfiguration:
    """
    Removed, see ``panel.io.django.get_asgi_application``.
    """

    def __init__(self, *args, **kwargs) -> None:
        raise RuntimeError(_CHANNELS_REMOVED.format(name='RoutingConfiguration'))


class DjangoBokehConfig:
    """
    Removed, Panel applications no longer have to be installed as a Django
    app, see ``panel.io.django.get_asgi_application``.
    """

    def __init__(self, *args, **kwargs) -> None:
        raise RuntimeError(_CHANNELS_REMOVED.format(name='DjangoBokehConfig'))


DocConsumer = _removed('DocConsumer')
AutoloadJsConsumer = _removed('AutoloadJsConsumer')
WSConsumer = _removed('WSConsumer')
