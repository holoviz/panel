"""
Subclasses the bokeh serve commandline handler to extend it in various
ways.
"""

import ast
import base64
import logging # isort:skip
import os

from glob import glob
from types import ModuleType

from bokeh.command.subcommands.serve import Serve as _BkServe
from bokeh.command.util import build_single_handler_applications

from bokeh.application import Application
from bokeh.application.handlers.document_lifecycle import DocumentLifecycleHandler
from bokeh.application.handlers.function import FunctionHandler
from bokeh.server.contexts import ApplicationContext
from tornado.ioloop import PeriodicCallback, IOLoop
from tornado.web import StaticFileHandler

from ..auth import OAuthProvider
from ..config import config
from ..util import fullpath
from ..io.rest import REST_PROVIDERS
from ..io.reload import record_modules, watch
from ..io.server import INDEX_HTML, get_static_routes, set_curdoc
from ..io.state import state

log = logging.getLogger(__name__)


def _cleanup_doc(doc):
    for callback in doc.session_destroyed_callbacks:
        try:
            callback(None)
        except Exception:
            pass
    doc.callbacks._change_callbacks[None] = {}
    doc.destroy(None)


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
    return dict((parse_var(item) for item in items))


class AdminApplicationContext(ApplicationContext):

    def __init__(self, application, unused_timeout=15000, **kwargs):
        super().__init__(application, io_loop=IOLoop.current(), **kwargs)
        self._unused_timeout = unused_timeout
        self._cleanup_cb = None
        self._loop.add_callback(self.run_load_hook)

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

    args = _BkServe.args + (
        ('--static-dirs', dict(
            metavar="KEY=VALUE",
            nargs='+',
            help=("Static directories to serve specified as key=value "
                  "pairs mapping from URL route to static file directory.")
        )),
        ('--oauth-provider', dict(
            action = 'store',
            type   = str,
            help   = "The OAuth2 provider to use."
        )),
        ('--oauth-key', dict(
            action  = 'store',
            type    = str,
            help    = "The OAuth2 key to use",
        )),
        ('--oauth-secret', dict(
            action  = 'store',
            type    = str,
            help    = "The OAuth2 secret to use",
        )),
        ('--oauth-redirect-uri', dict(
            action  = 'store',
            type    = str,
            help    = "The OAuth2 redirect URI",
        )),
        ('--oauth-extra-params', dict(
            action  = 'store',
            type    = str,
            help    = "Additional parameters to use.",
        )),
        ('--oauth-jwt-user', dict(
            action  = 'store',
            type    = str,
            help    = "The key in the ID JWT token to consider the user.",
        )),
        ('--oauth-encryption-key', dict(
            action = 'store',
            type    = str,
            help    = "A random string used to encode the user information."
        )),
        ('--oauth-error-template', dict(
            action = 'store',
            type    = str,
            help    = "A random string used to encode the user information."
        )),
        ('--oauth-expiry-days', dict(
            action  = 'store',
            type    = float,
            help    = "Expiry off the OAuth cookie in number of days.",
            default = 1
        )),
        ('--rest-provider', dict(
            action = 'store',
            type   = str,
            help   = "The interface to use to serve REST API"
        )),
        ('--rest-endpoint', dict(
            action  = 'store',
            type    = str,
            help    = "Endpoint to store REST API on.",
            default = 'rest'
        )),
        ('--rest-session-info', dict(
            action  = 'store_true',
            help    = "Whether to serve session info on the REST API"
        )),
        ('--session-history', dict(
            action  = 'store',
            type    = int,
            help    = "The length of the session history to record.",
            default = 0
        )),
        ('--warm', dict(
            action  = 'store_true',
            help    = "Whether to execute scripts on startup to warm up the server."
        )),
        ('--admin', dict(
            action  = 'store_true',
            help    = "Whether to add an admin panel."
        )),
        ('--profiler', dict(
            action  = 'store',
            type    = str,
            help    = "The profiler to use by default, e.g. pyinstrument or snakeviz."
        )),
        ('--autoreload', dict(
            action  = 'store_true',
            help    = "Whether to autoreload source when script changes."
        )),
        ('--num-threads', dict(
            action  = 'store',
            type    = int,
            help    = "Whether to start a thread pool which events are dispatched to.",
            default = None
        )),
        ('--setup', dict(
            action  = 'store',
            type    = str,
            help    = "Path to a setup script to run before server starts.",
            default = None
        ))
    )

    # Supported file extensions
    _extensions = ['.py']

    def customize_applications(self, args, applications):
        if args.index and not args.index.endswith('.html'):
            index = args.index.split(os.path.sep)[-1]
            for ext in self._extensions:
                if index.endswith(ext):
                    index = index[:-len(ext)]
            if f'/{index}' in applications:
                applications['/'] = applications[f'/{index}']
        return super().customize_applications(args, applications)

    def customize_kwargs(self, args, server_kwargs):
        '''Allows subclasses to customize ``server_kwargs``.

        Should modify and return a copy of the ``server_kwargs`` dictionary.
        '''
        kwargs = dict(server_kwargs)
        if 'index' not in kwargs:
            kwargs['index'] = INDEX_HTML

        # Handle tranquilized functions in the supplied functions
        kwargs['extra_patterns'] = patterns = kwargs.get('extra_patterns', [])

        static_dirs = parse_vars(args.static_dirs) if args.static_dirs else {}
        patterns += get_static_routes(static_dirs)

        files = []
        for f in args.files:
            if args.glob:
                files.extend(glob(f))
            else:
                files.append(f)

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

        # Handle tranquilized functions in the supplied functions
        if args.rest_provider in REST_PROVIDERS:
            pattern = REST_PROVIDERS[args.rest_provider](files, args.rest_endpoint)
            patterns.extend(pattern)
        elif args.rest_provider is not None:
            raise ValueError("rest-provider %r not recognized." % args.rest_provider)

        config.autoreload = args.autoreload

        if config.autoreload:
            for f in files:
                watch(f)

        if args.setup:
            setup_path = args.setup
            with open(setup_path) as f:
                setup_source = f.read()
            nodes = ast.parse(setup_source, os.fspath(setup_path))
            code = compile(nodes, filename=setup_path, mode='exec', dont_inherit=True)
            module_name = 'panel_setup_module'
            module = ModuleType(module_name)
            module.__dict__['__file__'] = fullpath(setup_path)
            exec(code, module.__dict__)
            state._setup_module = module

        if args.warm or args.autoreload:
            argvs = {f: args.args for f in files}
            applications = build_single_handler_applications(files, argvs)
            if args.autoreload:
                with record_modules():
                    for app in applications.values():
                        doc = app.create_document()
                        with set_curdoc(doc):
                            state._on_load(None)
                        _cleanup_doc(doc)
            else:
                for app in applications.values():
                    doc = app.create_document()
                    with set_curdoc(doc):
                        state._on_load(None)
                    _cleanup_doc(doc)

        prefix = args.prefix
        if prefix is None:
            prefix = ""
        prefix = prefix.strip("/")
        if prefix:
            prefix = "/" + prefix

        config.profiler = args.profiler
        if args.admin:
            from ..io.admin import admin_panel
            from ..io.server import per_app_patterns
            config._admin = True
            app = Application(FunctionHandler(admin_panel))
            unused_timeout = args.check_unused_sessions or 15000
            app_ctx = AdminApplicationContext(app, unused_timeout=unused_timeout, url='/admin')
            if all(not isinstance(handler, DocumentLifecycleHandler) for handler in app._handlers):
                app.add(DocumentLifecycleHandler())
            app_patterns = []
            for p in per_app_patterns:
                route = '/admin' + p[0]
                context = {"application_context": app_ctx}
                route = prefix + route
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
            patterns.extend(app_patterns)

        config.session_history = args.session_history
        if args.rest_session_info:
            pattern = REST_PROVIDERS['param'](files, 'rest')
            patterns.extend(pattern)
            state.publish('session_info', state, ['session_info'])

        if args.num_threads is not None:
            if config.nthreads is not None:
                raise ValueError(
                    "Supply num_threads either using the environment variable "
                    "PANEL_NUM_THREADS or as an explicit argument, not both."
                )
            config.nthreads = args.num_threads

        if args.oauth_provider:
            config.oauth_provider = args.oauth_provider
            config.oauth_expiry = args.oauth_expiry_days
            if config.oauth_key and args.oauth_key:
                raise ValueError(
                    "Supply OAuth key either using environment variable "
                    "or via explicit argument, not both."
                )
            elif args.oauth_key:
                config.oauth_key = args.oauth_key
            elif not config.oauth_key:
                raise ValueError(
                    "When enabling an OAuth provider you must supply "
                    "a valid oauth_key either using the --oauth-key "
                    "CLI argument or PANEL_OAUTH_KEY environment "
                    "variable."
                )

            if config.oauth_secret and args.oauth_secret:
                raise ValueError(
                    "Supply OAuth secret either using environment variable "
                    "or via explicit argument, not both."
                )
            elif args.oauth_secret:
                config.oauth_secret = args.oauth_secret
            elif not config.oauth_secret:
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
                                     "truncate the returned string.")
                if len(key) != 32:
                    raise ValueError(
                        "OAuth encryption key must be 32 url-safe "
                        "base64-encoded bytes."
                    )
                config.oauth_encryption_key = encryption_key
            elif not config.oauth_encryption_key:
                print("WARNING: OAuth has not been configured with an "
                      "encryption key and will potentially leak "
                      "credentials in cookies and a JWT token embedded "
                      "in the served website. Use at your own risk or "
                      "generate a key with the `panel oauth-key` CLI "
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
                    )
                state.encryption = Fernet(config.oauth_encryption_key)

            if args.cookie_secret and config.cookie_secret:
                raise ValueError(
                    "Supply cookie secret either using environment "
                    "variable or via explicit argument, not both."
                )
            elif args.cookie_secret:
                config.cookie_secret = args.cookie_secret
            elif not config.cookie_secret:
                raise ValueError(
                    "When enabling an OAuth provider you must supply "
                    "a valid cookie_secret either using the --cookie-secret "
                    "CLI argument or the PANEL_COOKIE_SECRET environment "
                    "variable."
                )
            kwargs['auth_provider'] = OAuthProvider(error_template=args.oauth_error_template)

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

        if config.cookie_secret:
            kwargs['cookie_secret'] = config.cookie_secret

        return kwargs
