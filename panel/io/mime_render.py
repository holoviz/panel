from __future__ import annotations

import ast
import base64
import copy
import io
import json

from html import escape
from typing import (
    TYPE_CHECKING, Any, Dict, Tuple,
)

from bokeh import __version__
from bokeh.document import Document
from bokeh.embed.util import standalone_docs_json_and_render_items

from ..viewable import Viewable
from .state import state

if TYPE_CHECKING:
    from bokeh.model import Model

#---------------------------------------------------------------------
# Execution API
#---------------------------------------------------------------------

def _convert_expr(expr: ast.Expr) -> ast.Expression:
    """
    Converts an ast.Expr to and ast.Expression that can be compiled
    and evaled.
    """
    expr.lineno = 0
    expr.col_offset = 0
    return ast.Expression(expr.value, lineno=0, col_offset = 0)

def exec_with_return(code: str, global_context: Dict[str, Any] = None) -> Any:
    """
    Executes a code snippet and returns the resulting output of the
    last line.

    Arguments
    ---------
    code: str
      The code to execute
    global_context: Dict[str, Any]
      The globals to inject into the execution context.

    Returns
    -------
    The return value of the executed code.
    """
    global_context = global_context if global_context else globals()
    code_ast = ast.parse(code)

    init_ast = copy.deepcopy(code_ast)
    init_ast.body = code_ast.body[:-1]

    last_ast = copy.deepcopy(code_ast)
    last_ast.body = code_ast.body[-1:]

    exec(compile(init_ast, "<ast>", "exec"), global_context)
    if type(last_ast.body[0]) == ast.Expr:
        return eval(compile(_convert_expr(last_ast.body[0]), "<ast>", "eval"), global_context)
    else:
        exec(compile(last_ast, "<ast>", "exec"), global_context)

#---------------------------------------------------------------------
# MIME Render API
#---------------------------------------------------------------------


MIME_METHODS = {
    "__repr__": "text/plain",
    "_repr_html_": "text/html",
    "_repr_markdown_": "text/markdown",
    "_repr_svg_": "image/svg+xml",
    "_repr_png_": "image/png",
    "_repr_pdf_": "application/pdf",
    "_repr_jpeg_": "image/jpeg",
    "_repr_latex": "text/latex",
    "_repr_json_": "application/json",
    "_repr_javascript_": "application/javascript",
    "savefig": "image/png",
    "servable": ""
}

def render_image(mime, value, meta):
    data = f"data:{mime};charset=utf-8;base64,{value}"
    attrs = " ".join(['{k}="{v}"' for k, v in meta.items()])
    return f'<img src="{data}" {attrs}</img>'

def identity(value, meta):
    return value

def escaped(value, meta):
    return escape(value)

MIME_RENDERERS = {
    "text/plain": escaped,
    "text/html": escaped,
    "image/png": lambda value, meta: render_image("image/png", value, meta),
    "image/jpeg": lambda value, meta: render_image("image/jpeg", value, meta),
    "image/svg+xml": identity,
    "application/json": identity,
    "application/javascript": lambda value, meta: f"<script>{value}</script>",
}


def _model_json(model: Model, target: str) -> Tuple[Document, str]:
    """
    Renders a Bokeh Model to JSON representation given a particular
    DOM target and returns the Document and the serialized JSON string.

    Arguments
    ---------
    model: bokeh.model.Model
        The bokeh model to render.
    target: str
        The id of the DOM node to render to.

    Returns
    -------
    document: Document
        The bokeh Document containing the rendered Bokeh Model.
    model_json: str
        The serialized JSON representation of the Bokeh Model.
    """
    doc = Document()
    model.server_doc(doc=doc)
    model = doc.roots[0]
    docs_json, _ = standalone_docs_json_and_render_items(
        [model], suppress_callback_warning=True
    )

    doc_json = list(docs_json.values())[0]
    root_id = doc_json['roots']['root_ids'][0]

    return doc, json.dumps(dict(
        target_id = target,
        root_id   = root_id,
        doc       = doc_json,
        version   = __version__,
    ))

def eval_formatter(obj, print_method):
    """
    Evaluates a formatter method.
    """
    if print_method == "__repr__":
        return repr(obj)
    elif hasattr(obj, print_method):
        if print_method == "savefig":
            buf = io.BytesIO()
            obj.savefig(buf, format="png")
            buf.seek(0)
            return base64.b64encode(buf.read()).decode("utf-8")
        return getattr(obj, print_method)()
    elif print_method == "_repr_mimebundle_":
        return {}, {}
    return None

def format_mime(obj):
    """
    Formats object using _repr_x_ methods.
    """
    if isinstance(obj, str):
        return escape(obj), "text/plain"
    elif isinstance(obj, Viewable):
        from .pyodide import _model_json
        doc, out = _model_json(obj, 'output-${msg.id}')
        state.cache['${msg.id}'] = doc
        return out, 'application/panel'

    mimebundle = eval_formatter(obj, "_repr_mimebundle_")
    if isinstance(mimebundle, tuple):
        format_dict, _ = mimebundle
    else:
        format_dict = mimebundle

    output, not_available = None, []
    for method, mime_type in reversed(MIME_METHODS.items()):
        if mime_type in format_dict:
            output = format_dict[mime_type]
        else:
            output = eval_formatter(obj, method)

        if output is None:
            continue
        elif mime_type not in MIME_RENDERERS:
            not_available.append(mime_type)
            continue
        break
    if output is None:
        output = escape(repr(output))
        mime_type = "text/plain"
    elif isinstance(output, tuple):
        output, meta = output
    else:
        meta = {}
    return MIME_RENDERERS[mime_type](output, meta), mime_type
