"""
Subclasses the bokeh serve commandline handler to extend it in various
ways.
"""

import ast
import base64
import logging # isort:skip

from glob import glob

from bokeh.command.subcommands.serve import Serve as _BkServe
from bokeh.command.util import build_single_handler_applications

from ..auth import OAuthProvider
from ..config import config
from ..io.rest import REST_PROVIDERS
from ..io.reload import record_modules, watch
from ..io.server import INDEX_HTML, get_static_routes
from ..io.state import state

log = logging.getLogger(__name__)


def _cleanup_doc(doc):
    for callback in doc.session_destroyed_callbacks:
        try:
            callback(None)
        except Exception:
            pass
    doc._callbacks[None] = {}
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
        ('--autoreload', dict(
            action  = 'store_true',
            help    = "Whether to autoreload source when script changes."
        ))
    )

    def customize_kwargs(self, args, server_kwargs):
        '''Allows subclasses to customize ``server_kwargs``.

        Should modify and return a copy of the ``server_kwargs`` dictionary.
        '''
        kwargs = dict(server_kwargs)
        if 'index' not in kwargs:
            kwargs['index'] = INDEX_HTML

        # Handle tranquilized functions in the supplied functions
        kwargs['extra_patterns'] = patterns = kwargs.get('extra_patterns', [])

        if args.static_dirs:
            static_dirs = parse_vars(args.static_dirs)
            patterns += get_static_routes(static_dirs)

        files = []
        for f in args.files:
            if args.glob:
                files.extend(glob(f))
            else:
                files.append(f)

        if args.index and not args.index.endswith('.html') and not any(f.endswith(args.index) for f in files):
            raise ValueError("The --index argument must either specify a jinja2 "
                             "template with a .html file extension or select one "
                             "of the applications being served as the default. "
                             f"The specified application {args.index!r} could "
                             "not be found.")

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

        if args.warm or args.autoreload:
            argvs = {f: args.args for f in files}
            applications = build_single_handler_applications(files, argvs)
            if args.autoreload:
                with record_modules():
                    for app in applications.values():
                        doc = app.create_document()
                        _cleanup_doc(doc)
            else:
                for app in applications.values():
                    doc = app.create_document()
                    _cleanup_doc(doc)
                    
        config.session_history = args.session_history
        if args.rest_session_info:
            pattern = REST_PROVIDERS['param'](files, 'rest')
            patterns.extend(pattern)
            state.publish('session_info', state, ['session_info'])

        if args.oauth_provider:
            config.oauth_provider = args.oauth_provider
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
            else:
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
            else:
                raise ValueError(
                    "When enabling an OAuth provider you must supply "
                    "a valid cookie_secret either using the --cookie-secret "
                    "CLI argument or the PANEL_COOKIE_SECRET environment "
                    "variable."
                )
            kwargs['auth_provider'] = OAuthProvider()

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
