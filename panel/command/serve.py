"""
Subclasses the bokeh serve commandline handler to extend it in various
ways.
"""
from __future__ import annotations

import ast
import base64
import contextlib
import importlib
import logging
import os
import pathlib
import sys
import typing as t

from glob import glob
from types import ModuleType

from bokeh.application import Application
from bokeh.application.handlers.document_lifecycle import (
    DocumentLifecycleHandler,
)
from bokeh.application.handlers.function import FunctionHandler
from bokeh.command.subcommand import Argument
from bokeh.command.subcommands.serve import (
    Serve as _BkServe, log as bk_serve_log,
)
from bokeh.command.util import build_single_handler_applications, die
from bokeh.core.validation import silence
from bokeh.core.validation.warnings import EMPTY_LAYOUT
from bokeh.resources import server_url
from bokeh.server.contexts import ApplicationContext
from bokeh.server.util import create_hosts_allowlist
from bokeh.settings import settings
from bokeh.util.logconfig import basicConfig
from tornado.ioloop import PeriodicCallback
from tornado.web import StaticFileHandler

from ..auth import BasicAuthProvider, OAuthProvider
from ..config import config
from ..io.document import _cleanup_doc
from ..io.liveness import LivenessHandler
from ..io.reload import record_modules, watch
from ..io.resources import DIST_DIR
from ..io.rest import REST_PROVIDERS
from ..io.server import INDEX_HTML, get_static_routes, set_curdoc
from ..io.state import state
from ..util import edit_readonly, fullpath

if t.TYPE_CHECKING:
    import argparse

    from collections.abc import Iterator

log = logging.getLogger(__name__)


@contextlib.contextmanager
def add_sys_path(path: str | os.PathLike) -> Iterator[None]:
    """Temporarily add the given path to `sys.path`."""
    path = os.fspath(path)
    try:
        sys.path.insert(0, path)
        yield
    finally:
        sys.path.remove(path)

def parse_var(s):
    """
    Parse a key, value pair, separated by '='
    That's the reverse of ShellArgs.

    On the command line (argparse) a declaration will typically look like:
        foo=hello
    or
        foo="hello world"
    """
    items = s.split('=')
    key = items[0].strip() # we remove blanks around keys, as is logical
    if len(items) > 1:
        # rejoin the rest:
        value = '='.join(items[1:])
    return (key, value)


def parse_vars(items):
    """
    Parse a series of key-value pairs and return a dictionary
    """
    return dict(parse_var(item) for item in items)


def _uvicorn_server(uv_config, on_started):
    """
    Builds the uvicorn server, invoking ``on_started`` once it is actually
    accepting connections, i.e. once the port it bound is known.
    """
    import uvicorn

    class PanelUvicornServer(uvicorn.Server):

        async def startup(self, sockets=None):
            await super().startup(sockets=sockets)
            on_started(self)

    return PanelUvicornServer(uv_config)


def _bound_port(server) -> int | None:
    """
    The port the uvicorn server actually bound, which differs from the
    requested port when serving on port 0.
    """
    for listener in server.servers:
        for sock in listener.sockets:
            address = sock.getsockname()
            if isinstance(address, tuple) and len(address) >= 2:
                return address[1]
    return None


class AdminApplicationContext(ApplicationContext):

    def __init__(self, application, unused_timeout=15000, **kwargs):
        super().__init__(application, **kwargs)
        self._unused_timeout = unused_timeout
        self._cleanup_cb = None

    async def cleanup_sessions(self):
        await self._cleanup_sessions(self._unused_timeout)

    def run_load_hook(self):
        self._cleanup_cb = PeriodicCallback(self.cleanup_sessions, self._unused_timeout)
        self._cleanup_cb.start()
        super().run_load_hook()

    def run_unload_hook(self):
        if self._cleanup_cb:
            self._cleanup_cb.stop()
        super().run_unload_hook()


class Serve(_BkServe):

    args = (
        tuple((arg, arg_obj) for arg, arg_obj in _BkServe.args if arg != '--dev') + (
        ('--index-titles', Argument(
            metavar="KEY=VALUE",
            nargs='+',
            help= ("Custom titles to use for Multi Page Apps specified as "
                   "key=value pairs mapping from the application page slug "
                   "to the title to show on the Multi Page App index page."
                   ),
        )),
        ('--static-dirs', Argument(
            metavar="KEY=VALUE",
            nargs='+',
            help=("Static directories to serve specified as key=value "
                  "pairs mapping from URL route to static file directory.")
        )),
        ('--basic-auth', Argument(
            action = 'store',
            type   = str,
            help   = "Password or filepath to use with Basic Authentication."
        )),
        ('--cookie-path', Argument(
            action = 'store',
            type   = str,
            help   = "The path the cookies should apply to ."
        )),
        ('--oauth-provider', Argument(
            action = 'store',
            type   = str,
            help   = "The OAuth2 provider to use."
        )),
        ('--oauth-key', Argument(
            action  = 'store',
            type    = str,
            help    = "The OAuth2 key to use",
        )),
        ('--oauth-secret', Argument(
            action  = 'store',
            type    = str,
            help    = "The OAuth2 secret to use",
        )),
        ('--oauth-redirect-uri', Argument(
            action  = 'store',
            type    = str,
            help    = "The OAuth2 redirect URI",
        )),
        ('--oauth-extra-params', Argument(
            action  = 'store',
            type    = str,
            help    = "Additional parameters to use.",
        )),
        ('--oauth-jwt-user', Argument(
            action  = 'store',
            type    = str,
            help    = "The key in the ID JWT token to consider the user.",
        )),
        ('--oauth-encryption-key', Argument(
            action = 'store',
            type    = str,
            help    = "A random string used to encode the user information."
        )),
        ('--oauth-error-template', Argument(
            action = 'store',
            type    = str,
            help    = "A random string used to encode the user information."
        )),
        ('--oauth-expiry-days', Argument(
            action  = 'store',
            type    = float,
            help    = "Expiry off the OAuth cookie in number of days.",
            default = 1
        )),
        ('--oauth-refresh-tokens', Argument(
            action  = 'store_true',
            help    = "Whether to automatically OAuth access tokens when they expire.",
        )),
        ('--oauth-guest-endpoints', Argument(
            action  = 'store',
            nargs   = '*',
            help    = "List of endpoints that can be accessed as a guest without authenticating.",
        )),
        ('--oauth-optional', Argument(
            action  = 'store_true',
            help    = (
                "Whether the user will be forced to go through login flow "
                "or if they can access all applications as a guest."
            )
        )),
        ('--root-path', Argument(
            action  = 'store',
            type    = str,
            help    = "The root path can be used to handle cases where Panel is served behind a proxy."
        )),
        ('--login-endpoint', Argument(
            action  = 'store',
            type    = str,
            help    = "Endpoint to serve the authentication login page on."
        )),
        ('--logout-endpoint', Argument(
            action  = 'store',
            type    = str,
            help    = "Endpoint to serve the authentication logout page on."
        )),
        ('--auth-template', Argument(
            action  = 'store',
            type    = str,
            help    = "Template to serve when user is unauthenticated."
        )),
        ('--logout-template', Argument(
            action  = 'store',
            type    = str,
            help    = "Template to serve logout page."
        )),
        ('--basic-login-template', Argument(
            action  = 'store',
            type    = str,
            help    = "Template to serve for Basic Authentication login page."
        )),
        ('--rest-provider', Argument(
            action = 'store',
            type   = str,
            help   = "The interface to use to serve REST API"
        )),
        ('--rest-endpoint', Argument(
            action  = 'store',
            type    = str,
            help    = "Endpoint to store REST API on.",
            default = 'rest'
        )),
        ('--rest-session-info', Argument(
            action  = 'store_true',
            help    = "Whether to serve session info on the REST API"
        )),
        ('--session-history', Argument(
            action  = 'store',
            type    = int,
            help    = "The length of the session history to record.",
            default = 0
        )),
        ('--warm', Argument(
            action  = 'store_true',
            help    = "Whether to execute scripts on startup to warm up the server."
        )),
        ('--admin', Argument(
            action  = 'store_true',
            help    = "Whether to add an admin panel."
        )),
        ('--admin-endpoint', Argument(
            action = 'store',
            type    = str,
            help    = "Name to use for the admin endpoint.",
            default = None
        )),
        ('--admin-log-level', Argument(
            action  = 'store',
            default = None,
            choices = ('debug', 'info', 'warning', 'error', 'critical'),
            help    = "One of: debug (default), info, warning, error or critical",
        )),
        ('--profiler', Argument(
            action  = 'store',
            type    = str,
            help    = "The profiler to use by default, e.g. pyinstrument, snakeviz or memray."
        )),
        ('--dev', Argument(
            action  = 'store_true',
            help    = "Whether to enable dev mode. Equivalent to --autoreload."
        )),
        ('--autoreload', Argument(
            action  = 'store_true',
            help    = "Whether to autoreload source when script changes. We recommend using --dev instead."
        )),
        ('--num-threads', Argument(
            action  = 'store',
            type    = int,
            help    = "Whether to start a thread pool which events are dispatched to.",
            default = None
        )),
        ('--setup', Argument(
            action  = 'store',
            type    = str,
            help    = "Path to a setup script to run before server starts. If --num-procs is enabled it will be run in each process after the server has started.",
            default = None
        )),
        ('--liveness', Argument(
            action  = 'store_true',
            help    = "Whether to add a liveness endpoint."
        )),
        ('--liveness-endpoint', Argument(
            action  = 'store',
            type    = str,
            help    = "The endpoint for the liveness API.",
            default = "liveness"
        )),
        ('--plugins', dict(
            action  = 'append',
            type    = str
        )),
        ('--reuse-sessions', Argument(
            action  = 'store',
            help    = "Whether to reuse sessions when serving the initial request.",
            default = False,
            const   = True,
            nargs   = "?"
        )),
        ('--global-loading-spinner', Argument(
            action  = 'store_true',
            help    = "Whether to add a global loading spinner to the application(s).",
        )),
        ('--server', Argument(
            action  = 'store',
            type    = str,
            default = 'tornado',
            choices = ['tornado', 'fastapi', 'asgi'],
            help    = (
                "The server implementation to serve the application(s) with. "
                "'tornado' serves on the Bokeh/Tornado server, 'asgi' and "
                "'fastapi' serve the ASGI application on uvicorn."
            )
        )),
    )) # type: ignore[assignment, ty:invalid-assignment]

    # Arguments which are implemented with Tornado request handlers and
    # therefore cannot be served by the ASGI implementations.
    _tornado_only_args: t.ClassVar[dict[str, str]] = {
        'plugins': '--plugins',
        'rest_provider': '--rest-provider',
        'rest_session_info': '--rest-session-info',
        'enable_xsrf_cookies': '--enable-xsrf-cookies',
    }

    # The server arguments the ASGI implementations understand, i.e. those
    # accepted by BokehServerCore and PanelASGI.
    _asgi_args: t.ClassVar[tuple[str, ...]] = (
        'auth_provider', 'check_unused_sessions_milliseconds', 'exclude_cookies',
        'exclude_headers', 'generate_session_ids', 'ico_path', 'include_cookies',
        'include_headers', 'index', 'keep_alive_milliseconds',
        'mem_log_frequency_milliseconds', 'prefix', 'secret_key',
        'session_token_expiration', 'sign_sessions',
        'stats_log_frequency_milliseconds',
        'unused_session_lifetime_milliseconds',
    )

    # Supported file extensions
    _extensions = ['.py', '.ipynb', '.md']

    # State shared between _configure_panel and the route/server construction
    _admin_path = '/admin'
    _files: list[str] = []
    _static_dirs: dict[str, str] = {}

    def customize_applications(self, args, applications):
        if args.index and not args.index.endswith('.html'):
            index = args.index.split(os.path.sep)[-1]
            for ext in self._extensions:
                if index.endswith(ext):
                    index = index[:-len(ext)]
            if f'/{index}' in applications:
                applications['/'] = applications[f'/{index}']
        return super().customize_applications(args, applications)

    def warm_applications(self, applications, reuse_sessions, error=True, initialize_session=True, index=None):
        from ..io.session import generate_session
        for path, app in applications.items():
            try:
                session = generate_session(app, initialize=initialize_session)
            except Exception as e:
                if error:
                    raise e
                else:
                    continue
            with set_curdoc(session.document):
                if config.session_key_func:
                    reuse_sessions = False
                else:
                    state._session_key_funcs[path] = lambda r: r.path
                    state._sessions[path] = session
                    if index and index.endswith('.py'):
                        index_path, _ = os.path.splitext(os.path.basename(index))
                        if path == f'/{index_path}':
                            state._sessions['/'] = session
                    session.block_expiration()
                state._on_load(None)
            _cleanup_doc(session.document, destroy=not reuse_sessions)

    def customize_kwargs(self, args, server_kwargs):
        '''Allows subclasses to customize ``server_kwargs``.

        Should modify and return a copy of the ``server_kwargs`` dictionary.
        '''
        kwargs = self._configure_panel(args, server_kwargs)
        self._tornado_routes(args, kwargs)
        return kwargs

    def _configure_panel(self, args, server_kwargs):
        '''Applies the transport neutral configuration.

        Mutates ``pn.config`` and ``pn.state`` as requested on the
        commandline and returns the server arguments every server
        implementation understands. The Tornado request handlers Panel
        serves alongside the applications are added by ``_tornado_routes``.
        '''
        kwargs = dict(server_kwargs)
        if 'index' not in kwargs:
            kwargs['index'] = INDEX_HTML
        elif kwargs['index'].endswith('.html'):
            kwargs['index'] = os.path.abspath(kwargs['index'])

        if args.ico_path:
            settings.ico_path.set_value(args.ico_path)
        else:
            kwargs["ico_path"] = DIST_DIR / "images" / "favicon.ico"

        self._static_dirs = parse_vars(args.static_dirs) if args.static_dirs else {}

        files = []
        for f in args.files:
            if args.glob:
                files.extend(glob(f))
            else:
                files.append(f)
        self._files = files

        if args.index and not args.index.endswith('.html'):
            found = False
            for ext in self._extensions:
                index = args.index if args.index.endswith(ext) else f'{args.index}{ext}'
                if any(f.endswith(index) for f in files):
                    found = True
            # Check for directory style applications
            for f in files:
                if '.' in os.path.basename(f): # Skip files with extension
                    continue
                if args.index == os.path.basename(f) or args.index == f:
                    found = True
            if not found:
                raise ValueError(
                    "The --index argument must either specify a jinja2 "
                    "template with a .html file extension or select one "
                    "of the applications being served as the default. "
                    f"The specified application {index!r} could not be "
                    "found."
                )

        # Handle custom titles for Multi Page Apps index
        if args.index_titles:
            for item in args.index_titles:
                slug, title = item.split('=', 1)
                config.index_titles[slug] = title

        config.global_loading_spinner = args.global_loading_spinner
        config.reuse_sessions = args.reuse_sessions

        if args.root_path:
            root_path = args.root_path
            if not root_path.endswith('/'):
                root_path += '/'
            if not root_path.startswith('/'):
                raise ValueError(
                    '--root-path must start with a leading slash (`/`).'
                )
            with edit_readonly(state):
                # The base URL is resolved against relative paths, so it has
                # to carry the trailing slash, i.e. --root-path /proxy must
                # not turn /app into /proxyapp.
                state.base_url = root_path

        if config.autoreload:
            for f in files:
                watch(f)

        if args.setup:
            module_name = 'panel_setup_module'
            module = ModuleType(module_name)
            module.__dict__['__file__'] = fullpath(args.setup)
            state._setup_module = module

            def setup_file():
                setup_path = state._setup_module.__dict__['__file__']
                with open(setup_path) as f:
                    setup_source = f.read()
                nodes = ast.parse(setup_source, os.fspath(setup_path))
                code = compile(nodes, filename=setup_path, mode='exec', dont_inherit=True)
                exec(code, state._setup_module.__dict__)

            if args.num_procs > 1:
                # We will run the setup_file for each process
                state._setup_file_callback = setup_file
            else:
                state._setup_file_callback = None
                setup_file()

        if args.warm or config.autoreload:
            argvs = {f: args.args for f in files}
            applications = build_single_handler_applications(files, argvs)
            if config.autoreload:
                with record_modules(list(applications.values())):
                    self.warm_applications(
                        applications, args.reuse_sessions, error=False, index=kwargs['index']
                    )
            else:
                self.warm_applications(applications, args.reuse_sessions, index=kwargs['index'])

        # Disable Tornado's autoreload
        if args.dev:
            server_kwargs.pop('autoreload', None)

        config.profiler = args.profiler
        if args.admin:
            from ..io.admin import admin_panel

            # If `--admin-endpoint` is not set, then we default to the `/admin` path.
            admin_path = "/admin"
            if args.admin_endpoint:
                admin_path = args.admin_endpoint
                admin_path = admin_path if admin_path.startswith('/') else f'/{admin_path}'
            self._admin_path = admin_path

            config._admin = True
            app = Application(FunctionHandler(admin_panel))
            unused_timeout = args.check_unused_sessions or 15000
            state._admin_context = AdminApplicationContext(
                app, unused_timeout=unused_timeout, url=admin_path
            )
            if all(not isinstance(handler, DocumentLifecycleHandler) for handler in app._handlers):
                app.add(DocumentLifecycleHandler())
            if args.admin_log_level is not None:
                if os.environ.get('PANEL_ADMIN_LOG_LEVEL'):
                    raise ValueError(
                        "admin_log_level supplied both using the environment variable "
                        "PANEL_ADMIN_LOG_LEVEL and as an explicit argument, only the "
                        "value supplied to the environment variable is used "
                    )
                else:
                    config.admin_log_level = args.admin_log_level.upper()

        config.session_history = args.session_history

        if args.num_threads is not None:
            if config.nthreads is not None:
                raise ValueError(
                    "Supply num_threads either using the environment variable "
                    "PANEL_NUM_THREADS or as an explicit argument, not both."
                )
            config.nthreads = args.num_threads

        if args.auth_template:
            authpath = pathlib.Path(args.auth_template)
            if not authpath.is_file():
                raise ValueError(
                    f"The supplied auth-template {args.auth_template} does not "
                    "exist, ensure you supply and existing Jinja2 template."
                )
            config.auth_template = str(authpath.absolute())

        if args.logout_template:
            logout_template = str(pathlib.Path(args.logout_template).absolute())
        else:
            logout_template = None

        if args.basic_auth and config.basic_auth:
            raise ValueError(
                "Turn on Basic authentication using environment variable "
                "or via explicit argument, not both"
            )

        if args.basic_login_template:
            login_template = args.basic_login_template
            authpath = pathlib.Path(login_template)
            if not authpath.is_file():
                raise ValueError(
                    f"The supplied auth-template {login_template} does not "
                    "exist, ensure you supply and existing Jinja2 template."
                )
        else:
            login_template = None

        login_endpoint = args.login_endpoint or '/login'
        login_endpoint = login_endpoint if login_endpoint.startswith('/') else f'/{login_endpoint}'
        logout_endpoint = args.logout_endpoint or '/logout'
        logout_endpoint = logout_endpoint if logout_endpoint.startswith('/') else f'/{logout_endpoint}'

        if args.oauth_error_template:
            error_template = str(pathlib.Path(args.oauth_error_template).absolute())
        elif config.auth_template:
            error_template = config.auth_template
        else:
            error_template = None

        if args.oauth_guest_endpoints:
            config.oauth_guest_endpoints = args.oauth_guest_endpoints
        if args.oauth_optional:
            config.oauth_optional = args.oauth_optional

        if args.basic_auth:
            config.basic_auth = args.basic_auth
        if config.basic_auth:
            kwargs['auth_provider'] = BasicAuthProvider(
                login_endpoint=login_endpoint,
                logout_endpoint=logout_endpoint,
                login_template=login_template,
                logout_template=logout_template,
                guest_endpoints=config.oauth_guest_endpoints,
            )

        if args.cookie_secret and config.cookie_secret:
            raise ValueError(
                "Supply cookie secret either using environment "
                "variable or via explicit argument, not both."
            )
        elif args.cookie_secret:
            config.cookie_secret = args.cookie_secret

        if args.cookie_path and "PANEL_COOKIE_PATH" in os.environ:
            raise ValueError(
                "Supply cookie path either using environment "
                "variable or via explicit argument, not both."
            )
        elif args.cookie_path:
            config.cookie_path = args.cookie_path

        # Check only one auth is used.
        if args.oauth_provider and config.oauth_provider:
                raise ValueError(
                    "Supply OAuth provider either using environment variable "
                    "or via explicit argument, not both."
                )

        if args.oauth_provider:
            config.oauth_provider = args.oauth_provider
        if config.oauth_provider:
            is_pam = config.oauth_provider
            config.oauth_refresh_tokens = args.oauth_refresh_tokens
            config.oauth_expiry = args.oauth_expiry_days
            if config.oauth_key and args.oauth_key:
                raise ValueError(
                    "Supply OAuth key either using environment variable "
                    "or via explicit argument, not both."
                )
            elif args.oauth_key:
                config.oauth_key = args.oauth_key
            elif not (config.oauth_key or is_pam):
                raise ValueError(
                    "When enabling an OAuth provider you must supply "
                    "a valid oauth_key either using the --oauth-key "
                    "CLI argument or PANEL_OAUTH_KEY environment "
                    "variable."
                )

            if not config.cookie_secret:
                raise ValueError(
                    "When enabling an OAuth provider you must supply "
                    "a valid cookie_secret either using the --cookie-secret "
                    "CLI argument or the PANEL_COOKIE_SECRET environment "
                    "variable."
                )

            if config.oauth_secret and args.oauth_secret:
                raise ValueError(
                    "Supply OAuth secret either using environment variable "
                    "or via explicit argument, not both."
                )
            elif args.oauth_secret:
                config.oauth_secret = args.oauth_secret
            elif not (config.oauth_secret or is_pam):
                raise ValueError(
                    "When enabling an OAuth provider you must supply "
                    "a valid OAuth secret either using the --oauth-secret "
                    "CLI argument or PANEL_OAUTH_SECRET environment "
                    "variable."
                )

            if args.oauth_extra_params:
                config.oauth_extra_params = ast.literal_eval(args.oauth_extra_params)

            if config.oauth_encryption_key and args.oauth_encryption_key:
                raise ValueError(
                    "Supply OAuth encryption key either using environment "
                    "variable or via explicit argument, not both."
                )
            elif args.oauth_encryption_key:
                encryption_key = args.oauth_encryption_key.encode('ascii')
                try:
                    key = base64.urlsafe_b64decode(encryption_key)
                except Exception:
                    raise ValueError("OAuth encryption key was not a valid base64 "
                                     "string. Generate an encryption key with "
                                     "`panel oauth-secret` and ensure you did not "
                                     "truncate the returned string.") from None
                if len(key) != 32:
                    raise ValueError(
                        "OAuth encryption key must be 32 url-safe "
                        "base64-encoded bytes."
                    )
                config.oauth_encryption_key = encryption_key
            elif not (config.oauth_encryption_key or is_pam):
                print("WARNING: OAuth has not been configured with an " # noqa: T201
                      "encryption key and will potentially leak "
                      "credentials in cookies and a JWT token embedded "
                      "in the served website. Use at your own risk or "
                      "generate a key with the `panel oauth-secret` CLI "
                      "command and then provide it to `panel serve` "
                      "using the PANEL_OAUTH_ENCRYPTION environment "
                      "variable or the --oauth-encryption-key CLI "
                      "argument.")

            if config.oauth_encryption_key:
                try:
                    from cryptography.fernet import Fernet
                except ImportError:
                    raise ImportError(
                        "Using OAuth2 provider with Panel requires the "
                        "cryptography library. Install it with `pip install "
                        "cryptography` or `conda install cryptography`."
                    ) from None
                state.encryption = Fernet(config.oauth_encryption_key)

            kwargs['auth_provider'] = OAuthProvider(
                login_endpoint=login_endpoint,
                logout_endpoint=logout_endpoint,
                login_template=login_template,
                logout_template=logout_template,
                error_template=error_template,
                guest_endpoints=config.oauth_guest_endpoints,
            )

            if args.oauth_redirect_uri and config.oauth_redirect_uri:
                raise ValueError(
                    "Supply OAuth redirect URI either using environment "
                    "variable or via explicit argument, not both."
                )
            elif args.oauth_redirect_uri:
                config.oauth_redirect_uri = args.oauth_redirect_uri

            if args.oauth_jwt_user and config.oauth_jwt_user:
                raise ValueError(
                    "Supply OAuth JWT user either using environment "
                    "variable or via explicit argument, not both."
                )
            elif args.oauth_jwt_user:
                config.oauth_jwt_user = args.oauth_jwt_user

        if config.cookie_path:
            kwargs['cookie_path'] = config.cookie_path

        if config.cookie_secret:
            kwargs['cookie_secret'] = config.cookie_secret

        return kwargs

    def _tornado_routes(self, args, kwargs):
        '''Adds the Tornado request handlers Panel serves alongside the apps.

        Everything registered here is implemented as a Tornado
        ``RequestHandler`` and therefore only applies to
        ``--server tornado``. The ASGI implementations serve the
        equivalent endpoints from ``panel.io.asgi.PanelASGI``.
        '''
        kwargs['extra_patterns'] = patterns = kwargs.get('extra_patterns', [])
        patterns += get_static_routes(self._static_dirs)

        # Handle tranquilized functions in the supplied functions
        if args.rest_provider in REST_PROVIDERS:
            patterns.extend(REST_PROVIDERS[args.rest_provider](self._files, args.rest_endpoint))
        elif args.rest_provider is not None:
            raise ValueError(f"rest-provider {args.rest_provider!r} not recognized.")

        if args.liveness:
            argvs = {f: args.args for f in self._files}
            applications = build_single_handler_applications(self._files, argvs)
            patterns += [(rf"/{args.liveness_endpoint}", LivenessHandler, dict(applications=applications))]

        if args.admin:
            patterns.extend(self._admin_patterns())

        if args.rest_session_info:
            patterns.extend(REST_PROVIDERS['param'](self._files, 'rest'))
            state.publish('session_info', state, ['session_info'])

        for plugin in (args.plugins or []):
            try:
                with add_sys_path('./'):
                    plugin_module = importlib.import_module(plugin)
            except ModuleNotFoundError as e:
                raise Exception(
                    f'Specified plugin module {plugin!r} could not be found. '
                    'Ensure the module exists and is in the right path. '
                ) from e
            try:
                routes = plugin_module.ROUTES
            except AttributeError as e:
                raise Exception(
                    f'The plugin module {plugin!r} does not declare '
                    'a ROUTES variable. Ensure that the module provides '
                    'a list of ROUTES to serve.'
                ) from e
            patterns.extend(routes)

        return patterns

    def _admin_patterns(self):
        '''Replicates the per-application routes for the admin application.

        On Tornado the admin application is not part of the applications the
        server was constructed with, so its document, websocket and autoload
        routes have to be registered by hand.
        '''
        from ..io.server import per_app_patterns

        app_ctx = state._admin_context
        admin_path = self._admin_path
        app_patterns = []
        for p in per_app_patterns:
            route = admin_path + p[0]
            context = {"application_context": app_ctx}
            app_patterns.append((route, p[1], context))

        websocket_path = None
        for r in app_patterns:
            if r[0].endswith("/ws"):
                websocket_path = r[0]
        if not websocket_path:
            raise RuntimeError("Couldn't find websocket path")
        for r in app_patterns:
            r[2]["bokeh_websocket_path"] = websocket_path
        try:
            import snakeviz
            SNAKEVIZ_PATH = os.path.join(os.path.dirname(snakeviz.__file__), 'static')
            app_patterns.append(
                ('/snakeviz/static/(.*)', StaticFileHandler, dict(path=SNAKEVIZ_PATH))
            )
        except Exception:
            pass
        return app_patterns

    def _asgi_applications(self, args):
        '''Builds the applications to serve, mirroring Bokeh's own invoke.'''
        files = []
        for f in args.files:
            if args.glob:
                files.extend(glob(f))
            else:
                files.append(f)
        argvs = {f: args.args for f in files}
        applications = build_single_handler_applications(files, argvs)
        if not applications:
            applications['/'] = Application()
        return self.customize_applications(args, applications)

    def _asgi_server_kwargs(self, args):
        '''Builds the ``BokehServerCore`` arguments requested on the CLI.'''
        # Rename the abbreviated arguments the same way Bokeh does
        for short, long in (
            ('keep_alive', 'keep_alive_milliseconds'),
            ('check_unused_sessions', 'check_unused_sessions_milliseconds'),
            ('unused_session_lifetime', 'unused_session_lifetime_milliseconds'),
            ('stats_log_frequency', 'stats_log_frequency_milliseconds'),
            ('mem_log_frequency', 'mem_log_frequency_milliseconds'),
        ):
            if (value := getattr(args, short, None)) is not None:
                setattr(args, long, value)

        server_kwargs = {
            key: getattr(args, key) for key in (
                'prefix', 'index', 'keep_alive_milliseconds',
                'check_unused_sessions_milliseconds',
                'unused_session_lifetime_milliseconds',
                'stats_log_frequency_milliseconds',
                'mem_log_frequency_milliseconds', 'include_cookies',
                'include_headers', 'exclude_cookies', 'exclude_headers',
                'session_token_expiration',
            ) if getattr(args, key, None) is not None
        }
        server_kwargs['sign_sessions'] = settings.sign_sessions()
        server_kwargs['secret_key'] = settings.secret_key_bytes()
        server_kwargs['generate_session_ids'] = True
        if args.session_ids == 'unsigned':
            server_kwargs['sign_sessions'] = False
        elif args.session_ids == 'signed':
            server_kwargs['sign_sessions'] = True
        elif args.session_ids == 'external-signed':
            server_kwargs['sign_sessions'] = True
            server_kwargs['generate_session_ids'] = False
        if server_kwargs['sign_sessions'] and not server_kwargs['secret_key']:
            die("To sign sessions, the BOKEH_SECRET_KEY environment variable must be set; "
                "the `bokeh secret` command can be used to generate a new key.")
        server_kwargs['ico_path'] = settings.ico_path(getattr(args, 'ico_path', None))
        return server_kwargs

    def _invoke_asgi(self, args: argparse.Namespace) -> None:
        '''Serves the application(s) as an ASGI application on uvicorn.'''
        try:
            import uvicorn
        except ImportError:
            raise ImportError(
                f"Serving with --server {args.server} requires uvicorn to be "
                "installed. Install it with `pip install uvicorn` or "
                "`conda install -c conda-forge uvicorn`."
            ) from None

        from ..io.asgi import PanelASGI

        basicConfig(format=args.log_format, filename=args.log_file)
        log_level = logging.INFO if (level := settings.py_log_level(args.log_level)) is None else level
        logging.getLogger('bokeh').setLevel(log_level)
        if args.use_config is not None:
            log.info(f"Using override config file: {args.use_config}")
            settings.load_config(args.use_config)

        for arg, flag in self._tornado_only_args.items():
            if getattr(args, arg, None):
                die(f"{flag} is implemented with Tornado request handlers and "
                    f"cannot be served with --server {args.server}. Use "
                    "--server tornado to enable it.")
        if args.num_procs != 1:
            die(f"--num-procs is not supported with --server {args.server}. "
                "Run multiple uvicorn worker processes behind a load balancer "
                "instead.")

        applications = self._asgi_applications(args)
        kwargs = self._configure_panel(args, self._asgi_server_kwargs(args))
        asgi_kwargs = {k: v for k, v in kwargs.items() if k in self._asgi_args}

        port = None if args.unix_socket else args.port
        ssl_certfile = settings.ssl_certfile(getattr(args, 'ssl_certfile', None))
        ssl_keyfile = settings.ssl_keyfile(getattr(args, 'ssl_keyfile', None))
        asgi_kwargs['extra_websocket_origins'] = create_hosts_allowlist(
            args.allow_websocket_origin, port
        )
        asgi_kwargs['absolute_url'] = server_url(args.address, port, bool(ssl_certfile))

        admin_context = state._admin_context if args.admin else None
        if admin_context is not None:
            applications[self._admin_path] = admin_context.application

        asgi = PanelASGI(
            applications,
            index_enabled=not args.disable_index,
            redirect_root=not args.disable_index_redirect,
            static_dirs=self._static_dirs,
            liveness=args.liveness_endpoint if args.liveness else False,
            **asgi_kwargs
        )
        if admin_context is not None:
            # Panel's AdminApplicationContext adds the periodic session
            # cleanup the admin dashboard depends on, so it replaces the
            # context BokehServerCore built for the admin application.
            asgi.core._applications[self._admin_path] = admin_context

        app: t.Any = asgi
        if args.server == 'fastapi':
            from ..io.fastapi import FastAPI, _install_panel_asgi
            app = FastAPI()
            _install_panel_asgi(app, asgi)

        uvicorn_kwargs: dict[str, t.Any] = {}
        if args.unix_socket:
            uvicorn_kwargs['uds'] = args.unix_socket
        else:
            uvicorn_kwargs['host'] = args.address or '0.0.0.0'  # noqa: S104
            uvicorn_kwargs['port'] = args.port
        if args.root_path:
            uvicorn_kwargs['root_path'] = args.root_path
        if args.websocket_max_message_size:
            uvicorn_kwargs['ws_max_size'] = args.websocket_max_message_size
        if ssl_certfile:
            uvicorn_kwargs['ssl_certfile'] = ssl_certfile
        if ssl_keyfile:
            uvicorn_kwargs['ssl_keyfile'] = ssl_keyfile
        if (ssl_password := settings.ssl_password()):
            uvicorn_kwargs['ssl_keyfile_password'] = ssl_password
        if args.use_xheaders:
            uvicorn_kwargs['proxy_headers'] = True
            uvicorn_kwargs['forwarded_allow_ips'] = '*'

        protocol = 'https' if ssl_certfile else 'http'
        address_string = args.address or 'localhost'
        prefix = asgi.core.prefix

        def on_started(server):
            # Log where Bokeh's own serve command logs. Panel's logger does not
            # propagate and is filtered by config.log_level, which would hide
            # the server startup messages.
            urls = []
            if (bound := _bound_port(server)) is not None:
                for route in sorted(applications):
                    url = f"{protocol}://{address_string}:{bound}{prefix}{route}"
                    bk_serve_log.info(f"Bokeh app running at: {url}")
                    urls.append(url)
            bk_serve_log.info(f"Starting Bokeh server with process id: {os.getpid()}")
            if args.show:
                from bokeh.util.browser import view
                for url in urls:
                    view(url, new='tab')

        uv_config = uvicorn.Config(app, **uvicorn_kwargs)
        _uvicorn_server(uv_config, on_started).run()

    def invoke(self, args: argparse.Namespace):
        # Autoreload must be enabled before the application(s) are executed
        # to avoid erroring out
        config.autoreload = args.autoreload or bool(args.dev)
        # Empty layout are valid and the Bokeh warning is silenced as usually
        # not relevant to Panel users.
        silence(EMPTY_LAYOUT, True)
        # dask.distributed changes the logging level of Bokeh, we will overwrite it
        # if the environment variable is not set to the default Bokeh level
        # See https://github.com/holoviz/panel/issues/2302
        if "DASK_DISTRIBUTED__LOGGING__BOKEH" not in os.environ:
            os.environ["DASK_DISTRIBUTED__LOGGING__BOKEH"] = "info"
        args.dev = None
        if getattr(args, 'server', 'tornado') == 'tornado':
            super().invoke(args)
        else:
            self._invoke_asgi(args)
