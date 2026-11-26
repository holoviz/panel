"""
Utilities for executing Python code and rendering the resulting output
using a similar MIME-type based rendering system as implemented by
IPython.

Attempts to limit the actual MIME types that have to be rendered on
to a minimum simplifying frontend implementation:

    - application/bokeh: Model JSON representation
    - text/plain: HTML escaped string output
    - text/html: HTML code to insert into the DOM
"""

from __future__ import annotations

import ast
import base64
import copy
import io
import sys
import traceback
import typing as t

from contextlib import redirect_stderr, redirect_stdout
from functools import cache
from html import escape
from importlib import metadata
from textwrap import dedent

#---------------------------------------------------------------------
# Import API
#---------------------------------------------------------------------

_GLOBAL_CONTEXT_EXEC: dict[str, t.Any] = {}
_STDLIBS = sys.stdlib_module_names
_PACKAGE_MAP = {
    'sklearn': 'scikit-learn',
    'skimage': 'scikit-image',
    'transformers_js': 'transformers-js-py',
}
_IGNORED_PKGS = ['js', 'pyodide', 'PIL']
_PANDAS_AUTODETECT = ['bokeh.sampledata', 'as_frame']

def _distribution_modules(distribution: str) -> tuple[set[str], set[str]]:
    modules = set()
    namespaces: set[str] = set()
    for file in metadata.files(distribution) or ():
        if file.suffix not in ('.py', '.pyc', '.pyd', '.so'):
            continue
        parents = file.parts[:-1]
        name = file.name.split('.', 1)[0]
        parts = parents if name == '__init__' else (*parents, name)
        modules.add('.'.join(parts))
        namespaces.update('.'.join(parts[:i]) for i in range(1, len(parts)))
    return modules, namespaces

def _find_distribution(
    module: str, member: str, root: str, distributions: list[str],
    get_modules: t.Callable[[str], tuple[set[str], set[str]]],
) -> str:
    if not distributions or distributions == [root]:
        return root
    providers = {name: get_modules(name) for name in distributions}
    owners = {name for name, (modules, _) in providers.items() if module in modules}
    if not owners and member and member != '*':
        submodule = f'{module}.{member}'
        owners = {
            name for name, (modules, namespaces) in providers.items()
            if submodule in modules or submodule in namespaces
        }
    if not owners:
        owners = {name for name, (_, namespaces) in providers.items() if module in namespaces}
    return next(iter(owners)) if len(owners) == 1 else root

def find_requirements(code: str) -> list[str]:
    """
    Finds the packages required in a string of code.

    Parameters
    ----------
    code : str
       the Python code to run.

    Returns
    -------
    ``List[str]``
        A list of package names that are to be installed for the code to be able to run.

    Examples
    --------
    >>> code = "import numpy as np; import scipy.stats"
    >>> find_requirements(code)
    ['numpy', 'scipy']
    """
    # handle mis-indented input from multi-line strings
    code = dedent(code)

    mod = ast.parse(code)
    imports: set[tuple[str, str]] = set()
    for node in ast.walk(mod):
        if isinstance(node, ast.Import):
            imports.update((name.name, '') for name in node.names)
        elif isinstance(node, ast.ImportFrom) and not node.level and node.module is not None:
            module = node.module
            imports.update((module, name.name) for name in node.names)

    packages = []
    distributions = None
    get_modules = cache(_distribution_modules)
    for module, member in sorted(imports):
        root = module.split('.', 1)[0]
        if root in _STDLIBS or root in _IGNORED_PKGS:
            continue
        pkg = _PACKAGE_MAP.get(root)
        if pkg is None:
            if distributions is None:
                distributions = metadata.packages_distributions()
            pkg = _find_distribution(module, member, root, distributions.get(root, []), get_modules)
        if isinstance(pkg, list):
            packages.extend(pkg)
        else:
            packages.append(pkg)
    if any(pdd in code for pdd in _PANDAS_AUTODETECT) and 'pandas' not in packages:
        packages.append('pandas')
    return list(dict.fromkeys(pkg for pkg in packages if pkg not in _IGNORED_PKGS))

#---------------------------------------------------------------------
# Execution API
#---------------------------------------------------------------------

class WriteCallbackStream(io.StringIO):

    def __init__(self, on_write=None, escape=True):
        self._onwrite = on_write
        self._escape = escape
        super().__init__()

    def write(self, s):
        if self._onwrite:
            self._onwrite(escape(s) if self._escape else s)
        super().write(s)

def _convert_expr(expr: ast.Expr) -> ast.Expression:
    """
    Converts an ast.Expr to an ast.Expression that can be compiled
    and evaled.
    """
    expr.lineno, expr.col_offset = 0, 0
    return ast.Expression(expr.value)

_OUT_BUFFER: list = []

def _display(*objs, **kwargs):
    """
    IPython.display compatibility wrapper.

    Note: This only handles a single display.
    """
    _OUT_BUFFER.extend(list(objs))

def exec_with_return(
    code: str,
    global_context: dict[str, t.Any] | None = None,
    stdout: t.IO | None = None,
    stderr: t.IO | None = None
) -> t.Any:
    """
    Executes a code snippet and returns the resulting output of the
    last line.

    Parameters
    ----------
    code: str
        The code to execute
    global_context: dict[str, Any] | None
        The globals to inject into the execution context.
    stdout: io.StringIO
        The stream to redirect stdout to.
    stderr: io.StringIO
        The stream to redirect stderr to.

    Returns
    -------

    The return value of the executed code.
    """
    global_context = global_context if global_context else _GLOBAL_CONTEXT_EXEC
    global_context['display'] = _display
    code_ast = ast.parse(code)

    init_ast = copy.deepcopy(code_ast)
    init_ast.body = code_ast.body[:-1]

    last_ast = copy.deepcopy(code_ast)
    last_ast.body = code_ast.body[-1:]

    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    with redirect_stdout(stdout), redirect_stderr(stderr):
        try:
            exec(compile(init_ast, "<ast>", "exec"), global_context)
            if not last_ast.body:
                out = None
            elif type(last_ast.body[0]) is ast.Expr:
                out = eval(compile(_convert_expr(last_ast.body[0]), "<ast>", "eval"), global_context)
            else:
                exec(compile(last_ast, "<ast>", "exec"), global_context)
                out = None
            if code.strip().endswith(';'):
                out = None
            if _OUT_BUFFER and out is None:
                out = _OUT_BUFFER[-1]
        except Exception:
            out = None
            traceback.print_exc(file=stderr)
        finally:
            _OUT_BUFFER.clear()
    return out

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
    "to_html": "text/html"
}

# Rendering function

def render_svg(value, meta, mime):
    return value, 'text/html'

def render_image(value, meta, mime):
    if isinstance(value, bytes):
        value = base64.b64encode(value).decode("utf-8")
    data = f"data:{mime};charset=utf-8;base64,{value}"
    attrs = " ".join([f'{k}="{v}"' for k, v in meta.items()])
    return f'<img src="{data}" {attrs}</img>', 'text/html'

def render_javascript(value, meta, mime):
    return f'<script>{value}</script>', 'text/html'

def render_markdown(value, meta, mime):
    import markdown
    return (markdown.markdown(
        value, extensions=["extra", "smarty", "codehilite"], output_format='html5'
    ), 'text/html')

def render_pdf(value, meta, mime):
    data = value.encode('utf-8')
    base64_pdf = base64.b64encode(data).decode("utf-8")
    src = f"data:application/pdf;base64,{base64_pdf}"
    return f'<embed src="{src}" width="100%" height="100%" type="application/pdf">', 'text/html'

def render_plotly(value, meta, mime):
    from ..pane import Plotly

    config = value.pop('config', {})
    return Plotly(value, config=config)

def identity(value, meta, mime):
    return value, mime

MIME_RENDERERS = {
    "image/png": render_image,
    "image/jpeg": render_image,
    "image/svg+xml": identity,
    "application/json": identity,
    "application/javascript": render_javascript,
    "application/pdf": render_pdf,
    "text/html": identity,
    "text/markdown": render_markdown,
    "text/plain": identity,
    "application/vnd.plotly.v1+json": render_plotly
}

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
    mimebundle = eval_formatter(obj, "_repr_mimebundle_")
    if isinstance(mimebundle, tuple):
        format_dict, _ = mimebundle
    else:
        format_dict = mimebundle

    output, not_available = None, []
    for method, mime_type in reversed(list(MIME_METHODS.items())):
        if mime_type in format_dict:
            output = format_dict[mime_type]
        elif isinstance(obj, type) and method != '__repr__':
            output = None
        else:
            output = eval_formatter(obj, method)

        if output is None:
            continue
        elif mime_type not in MIME_RENDERERS:
            not_available.append(mime_type)
            continue
        break
    if output is None:
        output = repr(output)
        mime_type = "text/plain"
    elif isinstance(output, tuple):
        output, meta = output
    else:
        meta = {}
    content, mime_type = MIME_RENDERERS[mime_type](output, meta, mime_type)
    if mime_type == 'text/plain':
        content = escape(content)
    return content, mime_type
