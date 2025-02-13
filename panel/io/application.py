"""
Extensions for Bokeh application handling.
"""
from __future__ import annotations

import json
import logging
import os

from collections.abc import Callable, Sequence
from functools import partial
from types import FunctionType, MethodType
from typing import TYPE_CHECKING, Any, TypeAlias
from urllib.parse import urljoin

import bokeh.command.util

from bokeh.application import Application as BkApplication
from bokeh.application.handlers.directory import DirectoryHandler
from bokeh.application.handlers.document_lifecycle import (
    DocumentLifecycleHandler,
)
from bokeh.application.handlers.function import FunctionHandler
from bokeh.models import CustomJS

from ..config import config
from .document import _destroy_document
from .handlers import MarkdownHandler, NotebookHandler, ScriptHandler
from .loading import LOADING_INDICATOR_CSS_CLASS
from .logging import LOG_SESSION_DESTROYED, LOG_SESSION_LAUNCHING
from .state import set_curdoc, state

if TYPE_CHECKING:
    from bokeh.application.application import SessionContext
    from bokeh.application.handlers.handler import Handler
    from bokeh.document.document import Document

    from ..template.base import BaseTemplate
    from ..viewable import Viewable, Viewer
    from .location import Location

    TViewable: TypeAlias = Viewable | Viewer | BaseTemplate
    TViewableFuncOrPath: TypeAlias = TViewable | Callable[[], TViewable] | os.PathLike | str


logger = logging.getLogger('panel.io.application')


def _eval_panel(
    panel: TViewableFuncOrPath, server_id: str | None, title: str,
    location: bool | Location, admin: bool, doc: Document
):
    from ..pane import panel as as_panel
    from ..template import BaseTemplate

    if config.global_loading_spinner:
        doc.js_on_event(
            'document_ready', CustomJS(code=f"""
            const body = document.getElementsByTagName('body')[0]
            body.classList.remove({LOADING_INDICATOR_CSS_CLASS!r}, {config.loading_spinner!r})
            """)
        )

    doc.on_event('document_ready', partial(state._schedule_on_load, doc))

    # Set up instrumentation for logging sessions
    logger.info(LOG_SESSION_LAUNCHING, id(doc))
    def _log_session_destroyed(session_context):
        logger.info(LOG_SESSION_DESTROYED, id(doc))
    doc.on_session_destroyed(_log_session_destroyed)

    with set_curdoc(doc):
        if isinstance(panel, (FunctionType, MethodType)):
            panel = panel()
        if isinstance(panel, BaseTemplate):
            doc = panel._modify_doc(server_id, title, doc, location)
        else:
            doc = as_panel(panel)._modify_doc(server_id, title, doc, location)
        return doc

def _on_session_destroyed(session_context: SessionContext) -> None:
    """
    Calls any on_session_destroyed callbacks defined on the Document
    """
    callbacks = session_context._document.session_destroyed_callbacks
    session_context._document.session_destroyed_callbacks = set()
    for callback in callbacks:
        try:
            callback(session_context)
        except Exception as e:
            logger.warning(
                "DocumentLifecycleHandler on_session_destroyed "
                f"callback {callback} failed with following error: {e}"
            )


class Application(BkApplication):
    """
    Extends Bokeh Application with ability to add global session
    creation callbacks, support for the admin dashboard and the
    ability to globally define a template.
    """

    def __init__(self, *args, **kwargs):
        self._admin = kwargs.pop('admin', None)
        super().__init__(*args, **kwargs)

    async def on_session_created(self, session_context):
        with set_curdoc(session_context._document):
            if self._admin is not None:
                config._admin = self._admin
            for cb in state._on_session_created_internal+state._on_session_created:
                cb(session_context)
        await super().on_session_created(session_context)

    def add(self, handler: Handler) -> None:
        """
        Override default DocumentLifeCycleHandler
        """
        if type(handler) is DocumentLifecycleHandler:
            handler._on_session_destroyed = _on_session_destroyed
        super().add(handler)

    def _set_session_prefix(self, doc):
        session_context = doc.session_context
        if not (session_context and session_context.server_context):
            return
        request = session_context.request
        app_context = session_context.server_context.application_context
        prefix = request.uri.replace(app_context._url, '')
        if not prefix.endswith('/'):
            prefix += '/'
        base_url = urljoin('/', prefix)
        rel_path = '/'.join(['..'] * app_context._url.strip('/').count('/'))

        # Handle autoload.js absolute paths
        abs_url = request.arguments.get('bokeh-absolute-url')
        if abs_url:
            rel_path = abs_url[0].decode('utf-8').replace(app_context._url, '')

        with set_curdoc(doc):
            state.base_url = base_url
            state.rel_path = rel_path

    def initialize_document(self, doc):
        logger.info(LOG_SESSION_LAUNCHING, id(doc))
        self._set_session_prefix(doc)
        super().initialize_document(doc)
        if doc in state._templates and doc not in state._templates[doc]._documents:
            template = state._templates[doc]
            with set_curdoc(doc):
                template.server_doc(title=template.title, location=True, doc=doc)
        def _log_session_destroyed(session_context):
            logger.info(LOG_SESSION_DESTROYED, id(doc))
        doc.destroy = partial(_destroy_document, doc) # type: ignore
        doc.on_event('document_ready', partial(state._schedule_on_load, doc))
        doc.on_session_destroyed(_log_session_destroyed)

    def process_request(self, request) -> dict[str, Any]:
        ''' Processes incoming HTTP request returning a dictionary of
        additional data to add to the session_context.

        Args:
            request: HTTP request

        Returns:
            A dictionary of JSON serializable data to be included on
            the session context.
        '''
        request_data = super().process_request(request)
        user = request.cookies.get('user')
        if user and config.cookie_secret:
            from tornado.web import decode_signed_value
            try:
                decoded = decode_signed_value(config.cookie_secret, 'user', user.value)
                if decoded:
                    user = decoded.decode('utf-8')
                else:
                    user = user.value
            except Exception:
                user = user.value
            if user in state._oauth_user_overrides:
                user_data = json.dumps(state._oauth_user_overrides[user])
                if state.encryption:
                    user_data = state.encryption.encrypt(user_data.encode('utf-8'))
                request_data['user_data'] = user_data
        return request_data

bokeh.command.util.Application = Application # type: ignore


def build_single_handler_application(path: str | os.PathLike, argv=None) -> Application:
    argv = argv or []
    path = os.path.abspath(os.path.expanduser(path))
    handler: Handler

    # There are certainly race conditions here if the file/directory is deleted
    # in between the isdir/isfile tests and subsequent code. But it would be a
    # failure if they were not there to begin with, too (just a different error)
    if os.path.isdir(path):
        handler = DirectoryHandler(filename=path, argv=argv)
    elif os.path.isfile(path):
        if path.endswith(".ipynb"):
            handler = NotebookHandler(filename=path, argv=argv)
        elif path.endswith(".md"):
            handler = MarkdownHandler(filename=path, argv=argv)
        elif path.endswith(".py"):
            handler = ScriptHandler(filename=path, argv=argv)
        else:
            raise ValueError(f"Expected a '.py' script or '.ipynb' notebook, got: {path!r}" % path)
    else:
        raise ValueError(f"Path for Bokeh server application does not exist: {path}")

    if handler.failed and not config.autoreload:
        raise RuntimeError(f"Error loading {path}:\n\n{handler.error}\n{handler.error_detail} ")

    application = Application(handler)

    return application

bokeh.command.util.build_single_handler_application = build_single_handler_application


def build_applications(
    panel: TViewableFuncOrPath | dict[str, TViewableFuncOrPath],
    title: str | dict[str, str] | None = None,
    location: bool | Location = True,
    admin: bool = False,
    server_id: str | None = None,
    custom_handlers: Sequence[Callable[[str, TViewableFuncOrPath], TViewableFuncOrPath]] | None = None
) -> dict[str, BkApplication]:
    """
    Converts a variety of objects into a dictionary of Applications.

    Parameters
    ----------
    panel: Viewable, function or {str: Viewable}
        A Panel object, a function returning a Panel object or a
        dictionary mapping from the URL slug to either.
    title : str or {str: str} (optional, default=None)
        An HTML title for the application or a dictionary mapping
        from the URL slug to a customized title.
    location : boolean or panel.io.location.Location
        Whether to create a Location component to observe and
        set the URL location.
    admin: boolean (default=False)
        Whether to enable the admin panel
    server_id: str
        ID of the server running the application(s)
    """
    if not isinstance(panel, dict):
        panel = {'/': panel}

    apps: dict[str, BkApplication] = {}
    for slug, app in panel.items():
        if slug.endswith('/') and slug != '/':
            raise ValueError(f"Invalid URL: trailing slash '/' used for {slug!r} not supported.")
        if isinstance(title, dict):
            try:
                title_ = title[slug]
            except KeyError:
                raise KeyError(
                    "Keys of the title dictionary and of the apps "
                    f"dictionary must match. No {slug} key found in the "
                    "title dictionary.") from None
        elif title:
            title_ = title
        else:
            title_ = 'Panel Application'
        slug = slug if slug.startswith('/') else '/'+slug

        # Handle other types of apps using a custom handler
        for custom_handler in (custom_handlers or ()):
            new_app = custom_handler(slug, app)
            if app is not None:
                break
        else:
            new_app = app
        if new_app is not None:
            app = new_app
            if app is True:
                continue

        if isinstance(app, os.PathLike):
            app = str(app) # enables serving apps from Paths
        if (isinstance(app, str) and app.endswith(('.py', '.ipynb', '.md'))
            and os.path.isfile(app)):
            apps[slug] = app = build_single_handler_application(app)
            app._admin = admin
        elif isinstance(app, BkApplication):
            apps[slug] = app
        else:
            handler = FunctionHandler(partial(_eval_panel, app, server_id, title_, location, admin))
            apps[slug] = Application(handler, admin=admin)

    if admin:
        if '/admin' in apps:
            raise ValueError(
                'Cannot enable admin panel because another app is being served '
                'on the /admin endpoint'
            )
        from .admin import admin_panel
        admin_handler = FunctionHandler(admin_panel)
        apps['/admin'] = Application(admin_handler)

    return apps
