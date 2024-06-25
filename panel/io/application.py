"""
Extensions for Bokeh application handling.
"""
from __future__ import annotations

import json
import logging
import os

from functools import partial
from typing import TYPE_CHECKING, Any

import bokeh.command.util

from bokeh.application import Application as BkApplication
from bokeh.application.handlers.directory import DirectoryHandler
from bokeh.application.handlers.document_lifecycle import (
    DocumentLifecycleHandler,
)

from ..config import config
from .document import _destroy_document
from .handlers import MarkdownHandler, NotebookHandler, ScriptHandler
from .logging import LOG_SESSION_DESTROYED, LOG_SESSION_LAUNCHING
from .state import set_curdoc, state

if TYPE_CHECKING:
    from bokeh.application.application import SessionContext
    from bokeh.application.handlers.handler import Handler

log = logging.getLogger('panel.io.application')


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
            log.warning("DocumentLifecycleHandler on_session_destroyed "
                        f"callback {callback} failed with following error: {e}")


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

    def initialize_document(self, doc):
        log.info(LOG_SESSION_LAUNCHING, id(doc))
        super().initialize_document(doc)
        if doc in state._templates and doc not in state._templates[doc]._documents:
            template = state._templates[doc]
            with set_curdoc(doc):
                template.server_doc(title=template.title, location=True, doc=doc)
        def _log_session_destroyed(session_context):
            log.info(LOG_SESSION_DESTROYED, id(doc))
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
        if user:
            from tornado.web import decode_signed_value
            try:
                user = decode_signed_value(config.cookie_secret, 'user', user.value).decode('utf-8')
            except Exception:
                user = user.value
            if user in state._oauth_user_overrides:
                user_data = json.dumps(state._oauth_user_overrides[user])
                if state.encryption:
                    user_data = state.encryption.encrypt(user_data.encode('utf-8'))
                request_data['user_data'] = user_data
        return request_data

bokeh.command.util.Application = Application # type: ignore


def build_single_handler_application(path, argv=None):
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

    if handler.failed:
        raise RuntimeError(f"Error loading {path}:\n\n{handler.error}\n{handler.error_detail} ")

    application = Application(handler)

    return application

bokeh.command.util.build_single_handler_application = build_single_handler_application
