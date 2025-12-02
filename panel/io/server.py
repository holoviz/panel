"""
Utilities for creating bokeh Server instances.
"""
from __future__ import annotations

import asyncio
import datetime as dt
import importlib
import inspect
import logging
import os
import pathlib
import signal
import sys
import threading
import uuid

from collections.abc import Callable, Mapping
from functools import partial, wraps
from html import escape
from typing import (
    TYPE_CHECKING, Any, Literal, TypedDict,
)
from urllib.parse import urlparse

import bokeh
import param
import tornado

# Bokeh imports
from bokeh.core.json_encoder import serialize_json
from bokeh.core.templates import AUTOLOAD_JS, FILE, MACROS
from bokeh.core.validation import silence
from bokeh.core.validation.warnings import EMPTY_LAYOUT
from bokeh.embed.bundle import Script
from bokeh.embed.elements import script_for_render_items
from bokeh.embed.util import RenderItem
from bokeh.embed.wrappers import wrap_in_script_tag
from bokeh.server.server import Server as BokehServer
from bokeh.server.urls import per_app_patterns, toplevel_patterns
from bokeh.server.views.autoload_js_handler import (
    AutoloadJsHandler as BkAutoloadJsHandler,
)
from bokeh.server.views.doc_handler import DocHandler as BkDocHandler
from bokeh.server.views.root_handler import RootHandler as BkRootHandler
from bokeh.server.views.static_handler import StaticHandler
from bokeh.util.serialization import make_id
from bokeh.util.token import (
    generate_jwt_token, generate_session_id, get_token_payload,
)
# Tornado imports
from tornado.ioloop import IOLoop
from tornado.web import (
    HTTPError, RequestHandler, StaticFileHandler, authenticated,
)
from tornado.wsgi import WSGIContainer

# Internal imports
from ..config import config
from ..util import edit_readonly, fullpath
from ..util.warnings import warn
from .application import build_applications
from .document import (  # noqa
    _cleanup_doc, init_doc, unlocked, with_lock,
)
from .liveness import LivenessHandler
from .loading import LOADING_INDICATOR_CSS_CLASS
from .logging import LOG_SESSION_CREATED
from .reload import record_modules
from .resources import (
    BASE_TEMPLATE, CDN_DIST, COMPONENT_PATH, DIST_DIR, ERROR_TEMPLATE,
    LOCAL_DIST, Resources, _env, bundle_resources, patch_model_css,
    resolve_custom_path,
)
from .session import generate_session
from .state import set_curdoc, state
from .threads import StoppableThread

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from bokeh.application.application import SessionContext
    from bokeh.core.types import ID
    from bokeh.document.document import DocJson
    from bokeh.embed.bundle import Bundle
    from bokeh.server.session import ServerSession
    from jinja2 import Template

    from .application import TViewableFuncOrPath
    from .location import Location

    class TokenPayload(TypedDict):
        headers: dict[str, Any]
        cookies: dict[str, Any]
        arguments: dict[str, Any]


#---------------------------------------------------------------------
# Private API
#---------------------------------------------------------------------

INDEX_HTML = os.path.join(os.path.dirname(__file__), '..', '_templates', "index.html")
DEFAULT_TITLE = "Panel Application"

def _origin_url(url: str) -> str:
    if url.startswith("http"):
        url = url.split("//")[1]
    return url

def _server_url(url: str, port: int) -> str:
    if url.startswith("http"):
        return f"{url.rsplit(':', 1)[0]}:{port}/"
    else:
        return f"http://{url.split(':')[0]}:{port}/"

_tasks = set()

def async_execute(func: Callable[..., None]) -> None:
    """
    Wrap async event loop scheduling to ensure that with_lock flag
    is propagated from function to partial wrapping it.
    """
    if not state.curdoc or not state.curdoc.session_context:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        # Avoid creating IOLoop if one is not already associated
        # with the asyncio loop or we're on a child thread
        if hasattr(IOLoop, '_ioloop_for_asyncio') and loop in IOLoop._ioloop_for_asyncio:
            ioloop = IOLoop._ioloop_for_asyncio[loop]
        elif threading.current_thread() is not threading.main_thread():
            ioloop = IOLoop.current()
        else:
            ioloop = None
        wrapper = state._handle_exception_wrapper(func)
        if loop.is_running():
            if ioloop is None:
                task = asyncio.ensure_future(wrapper())
                _tasks.add(task)
                task.add_done_callback(_tasks.discard)
            else:
                ioloop.add_callback(wrapper)
        else:
            loop.run_until_complete(wrapper())
        return

    if isinstance(func, partial) and hasattr(func.func, 'lock'):
        unlock = not func.func.lock # type: ignore
    else:
        unlock = not getattr(func, 'lock', False)
    curdoc = state.curdoc
    @wraps(func)
    async def wrapped(*args, **kw):
        with set_curdoc(curdoc):
            try:
                return await func(*args, **kw)
            except Exception as e:
                state._handle_exception(e)
    if unlock:
        wrapped.nolock = True # type: ignore
    state.curdoc.add_next_tick_callback(wrapped)

param.parameterized.async_executor = async_execute

def _initialize_session_info(session_context: SessionContext):
    from ..config import config
    session_id = session_context.id
    sessions = state.session_info['sessions']
    history = -1 if config._admin else config.session_history
    if not config._admin and (history == 0 or session_id in sessions):
        return

    state.session_info['total'] += 1
    if history > 0 and len(sessions) >= history:
        old_history = list(sessions.items())
        sessions = dict(old_history[-(history-1):])
        state.session_info['sessions'] = sessions
    request = session_context.request
    user_agent = request.headers.get('User-Agent') if request else None
    sessions[session_id] = {
        'launched': dt.datetime.now().timestamp(),
        'started': None,
        'rendered': None,
        'ended': None,
        'user_agent': user_agent
    }
    state.param.trigger('session_info')

state._on_session_created_internal.append(_initialize_session_info)

#---------------------------------------------------------------------
# Bokeh patches
#---------------------------------------------------------------------

def html_page_for_render_items(
    bundle: Bundle | tuple[str, str], docs_json: dict[ID, DocJson],
    render_items: list[RenderItem], title: str, template: Template | str | None = None,
    template_variables: dict[str, Any] = {}
) -> str:
    """
    Render an HTML page from a template and Bokeh render items.

    Parameters
    ----------
    bundle (tuple):
        A tuple containing (bokehjs, bokehcss)
    docs_json (JSON-like):
        Serialized Bokeh Document
    render_items (RenderItems)
        Specific items to render from the document and where
    title (str or None)
        A title for the HTML page. If None, DEFAULT_TITLE is used
    template (str or Template or None, optional) :
        A Template to be used for the HTML page. If None, FILE is used.
    template_variables (dict, optional):
        Any Additional variables to pass to the template

    Returns
    -------
    str
    """
    if title is None:
        title = DEFAULT_TITLE

    bokeh_js, bokeh_css = bundle

    json_id = make_id()
    json = escape(serialize_json(docs_json), quote=False)
    json = wrap_in_script_tag(json, "application/json", json_id)

    script = wrap_in_script_tag(script_for_render_items(json_id, render_items))

    context = template_variables.copy()

    context.update(dict(
        title = title,
        bokeh_js = bokeh_js,
        bokeh_css = bokeh_css,
        plot_script = json + script,
        docs = render_items,
        base = BASE_TEMPLATE,
        macros = MACROS,
    ))
    if "app_favicon" not in context:
        context["app_favicon"] = (f"{state.rel_path}/" if state.rel_path else "./") + "favicon.ico"

    if len(render_items) == 1:
        context["doc"] = context["docs"][0]
        context["roots"] = context["doc"].roots

    if template is None:
        tmpl = BASE_TEMPLATE
    elif isinstance(template, str):
        tmpl = _env.from_string("{% extends base %}\n" + template)
    else:
        tmpl = template

    html = tmpl.render(context)
    return html

def server_html_page_for_session(
    session: ServerSession,
    resources: Resources,
    title: str,
    token: str | None = None,
    template: str | Template = BASE_TEMPLATE,
    template_variables: dict[str, Any] | None = None,
) -> str:

    # ALERT: Replace with better approach before Bokeh 3.x compatible release
    if resources.mode == 'server':
        with set_curdoc(session.document):
            dist_url = f'{state.rel_path}/{LOCAL_DIST}' if state.rel_path else LOCAL_DIST
    else:
        dist_url = CDN_DIST

    doc = session.document
    doc._template_variables['theme_name'] = config.theme
    doc._template_variables['dist_url'] = dist_url
    for root in doc.roots:
        patch_model_css(root, dist_url=dist_url)

    render_item = RenderItem(
        token = token or session.token,
        roots = doc.roots,
        use_for_title = False,
    )

    if template_variables is None:
        template_variables = {}

    if template is FILE:
        template = BASE_TEMPLATE

    with set_curdoc(doc):
        bundle = bundle_resources(doc.roots, resources)
        html = html_page_for_render_items(
            bundle, {}, [render_item], title, template=template,
            template_variables=template_variables
        )
        if config.global_loading_spinner:
            html = html.replace(
                '<body>', f'<body class="{LOADING_INDICATOR_CSS_CLASS} pn-{config.loading_spinner}">'
            )
    return html


def autoload_js_script(doc, resources, token, element_id, app_path, absolute_url, absolute=False):
    resources = Resources.from_bokeh(resources, absolute=absolute)
    bundle = bundle_resources(doc.roots, resources)

    render_items = [RenderItem(token=token, elementid=element_id, use_for_title=False)]
    bundle.add(Script(script_for_render_items({}, render_items, app_path=app_path, absolute_url=absolute_url)))

    return AUTOLOAD_JS.render(bundle=bundle, elementid=element_id)


# Patch Server to attach task factory to asyncio loop and handle Admin server context
class Server(BokehServer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._autoreload_stop_event = None
        if state._admin_context:
            state._admin_context._loop = self._loop

    def start(self) -> None:
        super().start()
        if state._admin_context:
            self._loop.add_callback(state._admin_context.run_load_hook)
        if state._setup_module and state._setup_file_callback:
            self._loop.add_callback(state._setup_file_callback)
        if config.autoreload:
            from .reload import setup_autoreload_watcher
            self._autoreload_stop_event = stop_event = asyncio.Event()
            self._autoreload_task = self._loop.asyncio_loop.create_task(setup_autoreload_watcher(stop_event))

    def stop(self, wait: bool = True) -> None:
        if self._autoreload_stop_event:
            # For the stop event to be processed we have to restart
            # the IOLoop briefly, ensuring an orderly cleanup
            async def stop_autoreload():
                for event in state._watch_events:
                    event.set()
                state._watch_events = []
                self._autoreload_stop_event.set()
                await self._autoreload_task
            try:
                self._loop.asyncio_loop.run_until_complete(stop_autoreload())
            except RuntimeError:
                pass # Ignore if the event loop is still running
        super().stop(wait=wait)
        if state._admin_context:
            state._admin_context.run_unload_hook()

bokeh.server.server.Server = Server  # type: ignore

class LoginUrlMixin:
    """
    Overrides the AuthRequestHandler.get_login_url implementation to
    correctly handle prefixes.
    """

    def get_login_url(self):
        ''' Delegates to``get_login_url`` method of the auth provider, or the
        ``login_url`` attribute.

        '''
        if self.application.auth_provider.get_login_url is not None:
            return '.' + self.application.auth_provider.get_login_url(self)
        if self.application.auth_provider.login_url is not None:
            return '.' + self.application.auth_provider.login_url
        raise RuntimeError('login_url or get_login_url() must be supplied when authentication hooks are enabled')


class DocHandler(LoginUrlMixin, BkDocHandler):

    @authenticated  # type: ignore
    async def get_session(self) -> ServerSession:
        from ..config import config
        path = self.request.path
        session = None
        if config.reuse_sessions and path in state._session_key_funcs:
            key = state._session_key_funcs[path](self.request)
            session = state._sessions.get(key)
        if session is None:
            session = await super().get_session()  # type: ignore
            with set_curdoc(session.document):
                if config.reuse_sessions:
                    key_func = config.session_key_func or (lambda r: (r.path, r.arguments.get('theme', [b'default'])[0].decode('utf-8')))
                    state._session_key_funcs[path] = key_func
                    key = key_func(self.request)
                    state._sessions[key] = session
                    session.block_expiration()
        return session

    def _generate_token_payload(self) -> TokenPayload:
        app = self.application
        if app.include_headers is None:
            excluded_headers = (app.exclude_headers or [])
            allowed_headers = [header for header in self.request.headers
                               if header not in excluded_headers]
        else:
            allowed_headers = app.include_headers
        headers = {k: v for k, v in self.request.headers.items()
                   if k in allowed_headers}

        if app.include_cookies is None:
            excluded_cookies = (app.exclude_cookies or [])
            allowed_cookies = [cookie for cookie in self.request.cookies
                               if cookie not in excluded_cookies]
        else:
            allowed_cookies = app.include_cookies
        cookies = {k: v.value for k, v in self.request.cookies.items()
                   if k in allowed_cookies}

        if cookies and 'Cookie' in headers and 'Cookie' not in (app.include_headers or []):
            # Do not include Cookie header since cookies can be restored from cookies dict
            del headers['Cookie']

        arguments = {} if self.request.arguments is None else self.request.arguments
        payload: TokenPayload = {'headers': headers, 'cookies': cookies, 'arguments': arguments}
        payload.update(self.application_context.application.process_request(self.request))  # type: ignore
        return payload

    def _authorize(self, session: bool = False) -> tuple[bool | None, str | None]:
        """
        Determine if user is authorized to access this application.
        """
        auth_cb = config.authorize_callback
        # If inside a session ensure the authorize callback is not global
        if not auth_cb or (session and auth_cb is config._param__private.values['authorize_callback']):
            return True, None
        authorized = False
        auth_params = inspect.signature(auth_cb).parameters
        auth_args: tuple[dict[str, Any] | None] | tuple[dict[str, Any] | None, str]
        if len(auth_params) == 1:
            auth_args = (state.user_info,)
        elif len(auth_params) == 2:
            auth_args = (state.user_info, self.request.path,)
        else:
            raise RuntimeError(
                'Authorization callback must accept either 1) a single argument '
                'which is the user name or 2) two arguments which includes the '
                'user name and the url path the user is trying to access.'
            )
        auth_error: str | None = f'{state.user} is not authorized to access this application.'
        try:
            authorized = auth_cb(*auth_args)
            if isinstance(authorized, str):
                self.redirect(authorized)
                return None, None
            elif not authorized:
                auth_error = (
                    f'Access denied! User {state.user!r} is not authorized '
                    f'for the given app {self.request.path!r}.'
                )
            if authorized:
                auth_error = None
        except Exception:
            auth_error = f'Authorization callback errored. Could not validate user {state.user}.'
            logger.warning(auth_error)
        return authorized, auth_error

    def _render_auth_error(self, auth_error: str) -> str:
        if config.auth_template:
            with open(config.auth_template) as f:
                template = _env.from_string(f.read())
        else:
            template = ERROR_TEMPLATE
        return template.render(
            npm_cdn=config.npm_cdn,
            title='Panel: Authorization Error',
            error_type='Authorization Error',
            error='User is not authorized.',
            error_msg=auth_error
        )

    @authenticated
    async def get(self, *args, **kwargs):
        # Run global authorization callback
        payload = self._generate_token_payload()
        if config.authorize_callback:
            temp_session = generate_session(
                self.application, self.request, payload, initialize=False
            )
            with set_curdoc(temp_session.document):
                authorized, auth_error = self._authorize()
            if authorized is None:
                return
            elif not authorized:
                self.set_status(403)
                page = self._render_auth_error(auth_error)
                self.set_header("Content-Type", 'text/html')
                self.write(page)
                return

        app = self.application
        key_func = state._session_key_funcs.get(self.request.path, lambda r: r.path)
        old_request = key_func(self.request) in state._sessions
        session = await self.get_session()
        if old_request and state._sessions.get(key_func(self.request)) is session:
            session_id = generate_session_id(
                secret_key=self.application.secret_key,
                signed=self.application.sign_sessions
            )
            extra_payload = get_token_payload(session.token)
            extra_payload.update(payload)
            del extra_payload['session_expiry']
            token = generate_jwt_token(
                session_id,
                secret_key=app.secret_key,
                signed=app.sign_sessions,
                expiration=app.session_token_expiration,
                extra_payload=extra_payload
            )
            if config.reuse_sessions == 'warm':
                state.execute(
                    partial(
                        self.application_context.create_session_if_needed,
                        session_id,
                        self.request,
                        token
                    )
                )
        else:
            token = session.token
        logger.info(LOG_SESSION_CREATED, id(session.document))
        with set_curdoc(session.document):
            resources = Resources.from_bokeh(self.application.resources())
            # Session authorization callback
            authorized, auth_error = self._authorize(session=True)
            if authorized:
                page = server_html_page_for_session(
                    session, resources=resources, title=session.document.title,
                    token=token, template=session.document.template,
                    template_variables=session.document.template_variables,
                )
            elif authorized is None:
                return
            else:
                page = self._render_auth_error(auth_error)

        self.set_header("Content-Type", 'text/html')
        self.write(page)

per_app_patterns[0] = (r'/?', DocHandler)

# Patch Bokeh Autoload handler
class AutoloadJsHandler(BkAutoloadJsHandler):
    ''' Implements a custom Tornado handler for the autoload JS chunk

    '''

    async def get(self, *args, **kwargs) -> None:
        element_id = self.get_argument("bokeh-autoload-element", default=None)
        if not element_id:
            self.send_error(status_code=400, reason='No bokeh-autoload-element query parameter')
            return

        app_path = self.get_argument("bokeh-app-path", default="/")
        absolute_url = self.get_argument("bokeh-absolute-url", default=None)

        if absolute_url:
            server_url = f'{urlparse(absolute_url).scheme}://{urlparse(absolute_url).netloc}'
        else:
            server_url = None

        session = await self.get_session()  # type: ignore
        with set_curdoc(session.document):
            resources = Resources.from_bokeh(
                self.application.resources(server_url), absolute=True
            )
            js = autoload_js_script(
                session.document, resources, session.token, element_id,
                app_path, absolute_url, absolute=True
            )

        self.set_header("Content-Type", 'application/javascript')
        self.write(js)

per_app_patterns[3] = (r'/autoload.js', AutoloadJsHandler)

class RootHandler(LoginUrlMixin, BkRootHandler):
    """
    Custom RootHandler that provides the CDN_DIST directory as a
    template variable.
    """

    @authenticated
    async def get(self, *args, **kwargs):
        if self.use_redirect and len(self.applications) == 1:
            app_names = list(self.applications.keys())
            redirect_to = f".{app_names[0]}"
            self.redirect(redirect_to)
        else:
            if self.index is None:
                apps = sorted(self.applications.keys())
                index = "app_index.html"
            else:
                index = self.index
                apps = []
                for slug in self.applications.keys():
                    default_title = slug[1:]
                    slug = (
                        slug
                        if self.request.uri.endswith("/") or not self.prefix
                        else f"{self.prefix}{slug}"
                    )
                    # Try to get custom application page card title from config
                    # using as default value the application name
                    title = config.index_titles.get(slug, default_title)
                    apps.append((slug, title))
                apps = sorted(apps, key=lambda app: app[1])
            self.render(index, prefix=self.prefix, items=apps)

    def render(self, *args, **kwargs):
        kwargs['PANEL_CDN'] = CDN_DIST
        return super().render(*args, **kwargs)

toplevel_patterns[0] = (r'/?', RootHandler)
bokeh.server.tornado.RootHandler = RootHandler  # type: ignore


class AuthenticatedStaticFileHandler(StaticFileHandler):

    def get_login_url(self):
        ''' Delegates to``get_login_url`` method of the auth provider, or the
        ``login_url`` attribute.

        '''
        if self.application.auth_provider.get_login_url is not None:
            return self.application.auth_provider.get_login_url(self)
        if self.application.auth_provider.login_url is not None:
            return self.application.auth_provider.login_url
        raise RuntimeError('login_url or get_login_url() must be supplied when authentication hooks are enabled')

    def get_current_user(self):
        ''' Delegate to the synchronous ``get_user`` method of the auth
        provider

        '''
        if self.application.auth_provider.get_user is not None:
            return self.application.auth_provider.get_user(self)
        return "default_user"

    async def prepare(self):
        ''' Async counterpart to ``get_current_user``

        '''
        if self.application.auth_provider.get_user_async is not None:
            self.current_user = await self.application.auth_provider.get_user_async(self)

    @authenticated
    async def get(self, *args, **kwargs):
        return await super().get(*args, **kwargs)


# Copied from bokeh 2.4.0, to fix directly in bokeh at some point.
def create_static_handler(prefix, key, app):
    # patch
    key = '/__patchedroot' if key == '/' else key

    route = prefix
    route += "/static/(.*)" if key == "/" else key + "/static/(.*)"
    if app.static_path is not None:
        return (route, StaticFileHandler, {"path" : app.static_path})
    return (route, StaticHandler, {})

bokeh.server.tornado.create_static_handler = create_static_handler

#---------------------------------------------------------------------
# Async patches
#---------------------------------------------------------------------

# Bokeh 2.4.x patches the asyncio event loop policy but Tornado 6.1
# support the WindowsProactorEventLoopPolicy so we restore it,
# unless we detect we are running on jupyter_server.
# get_event_loop_policy, WindowsProactorEventLoopPolicy, WindowsProactorEventLoopPolicy
# is deprecated in Python 3.14.
if (
    sys.platform == 'win32' and
    sys.version_info < (3, 14, 0) and
    tornado.version_info >= (6, 1) and
    type(asyncio.get_event_loop_policy()) is asyncio.WindowsSelectorEventLoopPolicy and
    (('jupyter_server' not in sys.modules and
      'jupyter_client' not in sys.modules) or
     'pytest' in sys.modules)
):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------

class ComponentResourceHandler(StaticFileHandler):
    """
    A handler that serves local resources relative to a Python module.
    The handler resolves a specific Panel component by module reference
    and name, then resolves an attribute on that component to check
    if it contains the requested resource path.

    /<endpoint>/<module>/<class>/<attribute>/<path>
    """

    _resource_attrs = [
        '__css__', '__javascript__', '__js_module__', '__javascript_modules__',  '_resources',
        '_css', '_js', 'base_css', 'css', '_stylesheets', 'modifiers', '_bundle_path', '_bundle_css'
    ]

    def initialize(self, path: str | Literal['root'] = 'root', default_filename: str | None = None):
        self.root = path
        self.default_filename = default_filename

    def parse_url_path(self, path: str) -> str:
        """
        Resolves the resource the URL pattern refers to.
        """
        parts = path.split('/')
        if len(parts) < 4:
            raise HTTPError(400, 'Malformed URL')
        mod, cls, rtype, *subpath = parts
        try:
            module = importlib.import_module(mod)
        except ModuleNotFoundError:
            raise HTTPError(404, 'Module not found') from None
        try:
            component = getattr(module, cls)
        except AttributeError:
            raise HTTPError(404, 'Component not found') from None

        # May only access resources listed in specific attributes
        if rtype not in self._resource_attrs:
            raise HTTPError(403, 'Requested resource type not valid.')

        try:
            resources = getattr(component, rtype)
        except AttributeError:
            raise HTTPError(404, 'Resource type not found') from None

        # Handle template resources
        if rtype == '_resources':
            rtype = subpath[0]
            subpath = subpath[1:]
            if rtype not in resources:
                raise HTTPError(404, 'Resource type not found')
            resources = resources[rtype]
            rtype = f'_resources/{rtype}'
        elif rtype == 'modifiers':
            resources = [
                st for rs in resources.values() for st in rs.get('stylesheets', [])
                if isinstance(st, str)
            ]

        if isinstance(resources, dict):
            resources = list(resources.values())
        elif isinstance(resources, (str, pathlib.PurePath)):
            resources = [resources]
        resources = [
            str(resolve_custom_path(component, resource, relative=True)).replace(os.path.sep, '/')
            for resource in resources
        ]

        rel_path = '/'.join(subpath)

        # Important: May only access resources explicitly listed on the component
        # Otherwise this potentially exposes all files to the web
        if rel_path not in resources:
            raise HTTPError(403, 'Requested resource was not listed.')

        if not module.__file__:
            raise HTTPError(404, 'Requested module does not reference a file.')

        return str(pathlib.Path(module.__file__).parent / rel_path)

    @classmethod
    def get_absolute_path(cls, root: str, path: str) -> str:
        return path

    def validate_absolute_path(self, root: str, absolute_path: str) -> str:
        if not os.path.exists(absolute_path):
            raise HTTPError(404)
        if not os.path.isfile(absolute_path):
            raise HTTPError(403, "%s is not a file", self.path)
        return absolute_path


def serve(
    panels: TViewableFuncOrPath | dict[str, TViewableFuncOrPath],
    port: int = 0,
    address: str | None = None,
    websocket_origin: str | list[str] | None = None,
    loop: IOLoop | None = None,
    show: bool = True,
    start: bool = True,
    title: str | None = None,
    verbose: bool = True,
    location: bool = True,
    threaded: bool = False,
    admin: bool = False,
    **kwargs
) -> StoppableThread | Server:
    """
    Allows serving one or more panel objects on a single server.
    The panels argument should be either a Panel object or a function
    returning a Panel object or a dictionary of these two. If a
    dictionary is supplied the keys represent the slugs at which
    each app is served, e.g. `serve({'app': panel1, 'app2': panel2})`
    will serve apps at /app and /app2 on the server.

    Reference: https://panel.holoviz.org/user_guide/Server_Configuration.html#serving-multiple-apps

    Parameters
    ----------
    panels: Viewable, function or {str: Viewable or function}
      A Panel object, a function returning a Panel object or a
      dictionary mapping from the URL slug to either.
    port: int (optional, default=0)
      Allows specifying a specific port
    address : str
      The address the server should listen on for HTTP requests.
    websocket_origin: str or list(str) (optional)
      A list of hosts that can connect to the websocket.

      This is typically required when embedding a server app in
      an external web site.

      If None, "localhost" is used.
    loop : tornado.ioloop.IOLoop (optional, default=IOLoop.current())
      The tornado IOLoop to run the Server on
    show : boolean (optional, default=True)
      Whether to open the server in a new browser tab on start
    start : boolean(optional, default=True)
      Whether to start the Server
    title: str or {str: str} (optional, default=None)
      An HTML title for the application or a dictionary mapping
      from the URL slug to a customized title
    verbose: boolean (optional, default=True)
      Whether to print the address and port
    location : boolean or panel.io.location.Location
      Whether to create a Location component to observe and
      set the URL location.
    threaded: boolean (default=False)
      Whether to start the server on a new Thread
    admin: boolean (default=False)
      Whether to enable the admin panel
    kwargs: dict
      Additional keyword arguments to pass to Server instance
    """
    kwargs = dict(kwargs, **dict(
        port=port, address=address, websocket_origin=websocket_origin,
        loop=loop, show=show, start=start, title=title, verbose=verbose,
        location=location, admin=admin
    ))
    if threaded:
        kwargs['loop'] = loop = IOLoop(make_current=False) if loop is None else loop
        # To ensure that we have correspondence between state._threads and state._servers
        # we must provide a server_id here
        if 'server_id' not in kwargs:
            kwargs['server_id'] = uuid.uuid4().hex

        server = StoppableThread(
            target=get_server, io_loop=loop, args=(panels,), kwargs=kwargs
        )
        server_id = kwargs['server_id']
        state._threads[server_id] = server
        server.start()
    else:
        return get_server(panels, **kwargs)
    return server


class ProxyFallbackHandler(RequestHandler):
    """A `RequestHandler` that wraps another HTTP server callback and
    proxies the subpath.
    """

    def initialize(self, fallback, proxy=None):
        self.fallback = fallback
        self.proxy = proxy

    def prepare(self):
        if self.proxy:
            self.request.path = self.request.path.replace(self.proxy, '')
        self.fallback(self.request)
        self._finished = True
        self.on_finish()


def get_static_routes(static_dirs):
    """
    Returns a list of tornado routes of StaticFileHandlers given a
    dictionary of slugs and file paths to serve.
    """
    patterns = []
    for slug, path in static_dirs.items():
        if not slug.startswith('/'):
            slug = '/' + slug
        if slug == '/static':
            raise ValueError("Static file route may not use /static "
                             "this is reserved for internal use.")
        path = fullpath(path)
        if not os.path.isdir(path):
            raise ValueError(f"Cannot serve non-existent path {path}")
        patterns.append(
            (rf"{slug}/(.*)", AuthenticatedStaticFileHandler, {"path": path, "default_filename": "index.html"})
        )
    patterns.append((
        f'/{COMPONENT_PATH}(.*)', ComponentResourceHandler, {}
    ))
    return patterns

def get_server(
    panel: TViewableFuncOrPath | dict[str, TViewableFuncOrPath],
    port: int = 0,
    address: str | None = None,
    websocket_origin: str | list[str] | None = None,
    loop: IOLoop | None = None,
    show: bool = False,
    start: bool = False,
    title: str | dict[str, str] | None = None,
    verbose: bool = False,
    location: bool | Location = True,
    admin: bool = False,
    static_dirs: Mapping[str, str] = {},
    basic_auth: str | None = None,
    oauth_provider: str | None = None,
    oauth_key: str | None = None,
    oauth_secret: str | None = None,
    oauth_redirect_uri: str | None = None,
    oauth_extra_params: Mapping[str, str] = {},
    oauth_error_template: str | None = None,
    cookie_path: str  = "/",
    cookie_secret: str | None = None,
    oauth_encryption_key: str | None = None,
    oauth_jwt_user: str | None = None,
    oauth_refresh_tokens: str | None = None,
    oauth_guest_endpoints: list[str] | None = None,
    oauth_optional: bool | None = None,
    root_path: str | None = None,
    login_endpoint: str | None = None,
    logout_endpoint: str | None = None,
    login_template: str | None = None,
    logout_template: str | None = None,
    session_history: str | None = None,
    liveness: bool | str = False,
    warm: bool = False,
    **kwargs
) -> Server:
    """
    Returns a Server instance with this panel attached as the root
    app.

    Parameters
    ----------
    panel: Viewable, function or {str: Viewable}
      A Panel object, a function returning a Panel object or a
      dictionary mapping from the URL slug to either.
    port: int (optional, default=0)
      Allows specifying a specific port
    address : str
      The address the server should listen on for HTTP requests.
    websocket_origin: str or list(str) (optional)
      A list of hosts that can connect to the websocket.

      This is typically required when embedding a server app in
      an external web site.

      If None, "localhost" is used.
    loop : tornado.ioloop.IOLoop (optional, default=IOLoop.current())
      The tornado IOLoop to run the Server on.
    show : boolean (optional, default=False)
      Whether to open the server in a new browser tab on start.
    start : boolean(optional, default=False)
      Whether to start the Server.
    title : str or {str: str} (optional, default=None)
      An HTML title for the application or a dictionary mapping
      from the URL slug to a customized title.
    verbose: boolean (optional, default=False)
      Whether to report the address and port.
    location : boolean or panel.io.location.Location
      Whether to create a Location component to observe and
      set the URL location.
    admin: boolean (default=False)
      Whether to enable the admin panel
    static_dirs: dict (optional, default={})
      A dictionary of routes and local paths to serve as static file
      directories on those routes.
    basic_auth: str (optional, default=None)
      Password or filepath to use with basic auth provider.
    oauth_provider: str
      One of the available OAuth providers
    oauth_key: str (optional, default=None)
      The public OAuth identifier
    oauth_secret: str (optional, default=None)
      The client secret for the OAuth provider
    oauth_redirect_uri: Optional[str] = None,
      Overrides the default OAuth redirect URI
    oauth_extra_params: dict (optional, default={})
      Additional information for the OAuth provider
    oauth_error_template: str (optional, default=None)
      Jinja2 template used when displaying authentication errors.
    cookie_path: str (optional, default='/')
      The sub path of the domain the cookie is valid for.
    cookie_secret: str (optional, default=None)
      A random secret string to sign cookies (required for OAuth)
    oauth_encryption_key: str (optional, default=None)
      A random encryption key used for encrypting OAuth user
      information and access tokens.
    oauth_jwt_user: Optional[str] = None,
      Key that identifies the user in the JWT id_token.
    oauth_refresh_tokens: bool (optional, default=None)
      Whether to automatically refresh OAuth access tokens when they expire.
    oauth_guest_endpoints: list (optional, default=None)
      List of endpoints that can be accessed as a guest without authenticating.
    oauth_optional: bool (optional, default=None)
      Whether the user will be forced to go through login flow or if
      they can access all applications as a guest.
    root_path: str (optional, default=None)
      Root path the application is being served on when behind
      a reverse proxy.
    login_endpoint: str (optional, default=None)
      Overrides the default login endpoint `/login`
    logout_endpoint: str (optional, default=None)
      Overrides the default logout endpoint `/logout`
    logout_template: str (optional, default=None)
      Jinja2 template served when viewing the login endpoint when
      authentication is enabled.
    logout_template: str (optional, default=None)
      Jinja2 template served when viewing the logout endpoint when
      authentication is enabled.
    session_history: int (optional, default=None)
      The amount of session history to accumulate. If set to non-zero
      and non-None value will launch a REST endpoint at
      /rest/session_info, which returns information about the session
      history.
    liveness: bool | str (optional, default=False)
      Whether to add a liveness endpoint. If a string is provided
      then this will be used as the endpoint, otherwise the endpoint
      will be hosted at /liveness.
    warm: bool (optional, default=False)
      Whether to run the applications before serving them to ensure
      all imports and caches are fully warmed up before serving the app.
    kwargs: dict
      Additional keyword arguments to pass to Server instance.

    Returns
    -------
    server : panel.io.server.Server
      Bokeh Server instance running this panel
    """
    from ..config import config
    from .rest import REST_PROVIDERS

    silence(EMPTY_LAYOUT, True)
    server_id = kwargs.pop('server_id', uuid.uuid4().hex)
    kwargs['extra_patterns'] = extra_patterns = list(kwargs.get('extra_patterns', []))

    def flask_handler(slug, app):
        if 'flask' not in sys.modules:
            return
        from flask import Flask
        if not isinstance(app, Flask):
            return
        wsgi = WSGIContainer(app)
        if slug == '/':
            raise ValueError('Flask apps must be served on a subpath.')
        if not slug.endswith('/'):
            slug += '/'
        extra_patterns.append((
            f'^{slug}.*', ProxyFallbackHandler, dict(fallback=wsgi, proxy=slug)
        ))
        return True

    apps = build_applications(
        panel, title=title, location=location, admin=admin, custom_handlers=(flask_handler,)
    )

    if warm or config.autoreload:
        for endpoint, app in apps.items():
            if endpoint == '/admin':
                continue
            if config.autoreload:
                with record_modules(list(apps.values())):
                    session = generate_session(app)
            else:
                session = generate_session(app)
            with set_curdoc(session.document):
                state._on_load(None)
            _cleanup_doc(session.document, destroy=True)

    extra_patterns += get_static_routes(static_dirs)

    if session_history is not None:
        config.session_history = session_history
    if config.session_history != 0:
        pattern = REST_PROVIDERS['param']([], 'rest')
        extra_patterns.extend(pattern)
        state.publish('session_info', state, ['session_info'])

    if liveness:
        liveness_endpoint = 'liveness' if isinstance(liveness, bool) else liveness
        extra_patterns += [(rf"/{liveness_endpoint}", LivenessHandler, dict(applications=apps))]

    opts = dict(kwargs)
    if loop:
        asyncio.set_event_loop(loop.asyncio_loop)
        opts['io_loop'] = loop
    elif opts.get('num_procs', 1) == 1:
        opts['io_loop'] = IOLoop.current()

    if 'index' not in opts:
        opts['index'] = INDEX_HTML

    if 'ico_path' not in opts:
        opts['ico_path'] = DIST_DIR / "images" / "favicon.ico"

    if address is not None:
        opts['address'] = address

    if websocket_origin:
        if not isinstance(websocket_origin, list):
            websocket_origin = [websocket_origin]
        opts['allow_websocket_origin'] = websocket_origin

    # Configure OAuth
    from ..config import config
    server_config = {}
    login_template = kwargs.pop('basic_login_template', login_template)
    if basic_auth or oauth_provider:
        from ..auth import BasicAuthProvider, OAuthProvider
        if basic_auth:
            server_config['basic_auth'] = basic_auth
            provider = BasicAuthProvider
        else:
            config.oauth_provider = oauth_provider  # type: ignore
            provider = OAuthProvider
        opts['auth_provider'] = provider(
            login_endpoint=login_endpoint,
            logout_endpoint=logout_endpoint,
            login_template=login_template,
            logout_template=logout_template,
            error_template=oauth_error_template,
            guest_endpoints=oauth_guest_endpoints,
        )
    if oauth_key:
        config.oauth_key = oauth_key # type: ignore
    if oauth_secret:
        config.oauth_secret = oauth_secret # type: ignore
    if oauth_extra_params:
        config.oauth_extra_params = oauth_extra_params # type: ignore
    if cookie_path:
        config.cookie_path = cookie_path # type: ignore
    if cookie_secret:
        config.cookie_secret = cookie_secret # type: ignore
    if oauth_redirect_uri:
        config.oauth_redirect_uri = oauth_redirect_uri # type: ignore
    if oauth_refresh_tokens is not None:
        config.oauth_refresh_tokens = oauth_refresh_tokens  # type: ignore
    if oauth_optional is not None:
        config.oauth_optional = oauth_optional  # type: ignore
    if oauth_guest_endpoints is not None:
        config.oauth_guest_endpoints = oauth_guest_endpoints  # type: ignore
    if oauth_jwt_user is not None:
        config.oauth_jwt_user = oauth_jwt_user  # type: ignore
    if root_path:
        with edit_readonly(state):
            state.base_url = root_path  # type: ignore
    opts['cookie_path'] = config.cookie_path
    opts['cookie_secret'] = config.cookie_secret

    server = Server(apps, port=port, **opts)
    if verbose:
        address = server.address or 'localhost'
        url = f"http://{address}:{server.port}{server.prefix}"
        print(f"Launching server at {url}")  # noqa: T201

    state._servers[server_id] = (server, panel, [])
    state._server_config[server._tornado] = server_config

    if show:
        login_endpoint = login_endpoint or '/login'
        def show_callback():
            server.show(login_endpoint if config.oauth_provider or basic_auth else '/')
        server.io_loop.add_callback(show_callback)

    def sig_exit(*args, **kwargs):
        server.io_loop.asyncio_loop.call_soon_threadsafe(do_stop)

    def do_stop(*args, **kwargs):
        server.io_loop.stop()

    try:
        signal.signal(signal.SIGINT, sig_exit)
    except ValueError:
        pass # Can't use signal on a thread

    if start:
        server.start()
        try:
            server.io_loop.start()
        except RuntimeError:
            pass
        except TypeError:
            warn(
                "IOLoop couldn't be started. Ensure it is started by "
                "process invoking the panel.io.server.serve."
            )
    return server
