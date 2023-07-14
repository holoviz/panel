from __future__ import annotations

import os

from typing import IO

import bokeh.command.util

from bokeh.application.handlers.code import CodeHandler
from bokeh.command.util import (
    build_single_handler_application as _build_application,
)


def extract_code(
    filehandle: IO, supported_syntax: tuple[str, ...] = ('{pyodide}', 'python')
) -> str:
    """
    Extracts Panel application code from a Markdown file.
    """
    inblock = False
    block_opener = None
    title = None
    markdown = []
    out = []
    while True:
        line = filehandle.readline()
        if not line:
            # EOF
            break

        lsline = line.lstrip()
        if inblock:
            if lsline.startswith(block_opener):
                inblock = False
            else:
                out.append(line)
        elif lsline.startswith("```"):
            num_leading_backticks = len(lsline) - len(lsline.lstrip("`"))
            block_opener = '`'*num_leading_backticks
            syntax = line.strip()[num_leading_backticks:]
            if syntax in supported_syntax:
                if markdown:
                    md = ''.join(markdown)
                    markdown.clear()
                    if any('pn.extension' in o for o in out):
                        out.append(f"pn.pane.Markdown({md!r}).servable()\n")
                inblock = True
            else:
                markdown.append(line)
        elif line.startswith('# '):
            title = line[1:].lstrip()
        else:
            markdown.append(line)
    if markdown:
        md = ''.join(markdown)
        if any('pn.extension' in o for o in out):
            out.append(f"pn.pane.Markdown({md!r}).servable()\n")
    if title and any('template=' in o for o in out if 'pn.extension' in o):
        out.append(f'pn.state.template.title = {title.strip()!r}')
    return '\n'.join(out)

class MarkdownHandler(CodeHandler):
    ''' Modify Bokeh documents by creating Dashboard from a Markdown file.

    '''

    def __init__(self, *args, **kwargs):
        '''

        Keywords:
            filename (str) : a path to a Markdown (".md") file

        '''
        if 'filename' not in kwargs:
            raise ValueError('Must pass a filename to Handler')
        filename = os.path.abspath(kwargs['filename'])
        with open(filename, encoding='utf-8') as f:
            code = extract_code(f)
        kwargs['source'] = code
        super().__init__(*args, **kwargs)

def build_single_handler_application(path, argv=None):
    if not os.path.isfile(path) or not path.endswith(".md"):
        return _build_application(path, argv)

    from .server import Application
    handler = MarkdownHandler(filename=path)
    if handler.failed:
        raise RuntimeError("Error loading %s:\n\n%s\n%s " % (path, handler.error, handler.error_detail))

    application = Application(handler)

    return application

bokeh.command.util.build_single_handler_application = build_single_handler_application
