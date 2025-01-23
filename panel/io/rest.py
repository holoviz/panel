import json
import os
import tempfile
import traceback

from runpy import run_path
from unittest.mock import MagicMock
from urllib.parse import parse_qs

import param

from tornado import web
from tornado.wsgi import WSGIContainer

from ..entry_points import entry_points_for
from .state import state


class HTTPError(web.HTTPError):
    """
    Custom HTTPError type
    """


class BaseHandler(web.RequestHandler):

    def write_error(self, status_code, **kwargs):
        self.set_header('Content-Type', 'application/json')
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            lines = []
            for line in traceback.format_exception(*kwargs["exc_info"]):
                lines.append(line)
            self.finish(json.dumps({
                'error': {
                    'code': status_code,
                    'message': self._reason,
                    'traceback': lines,
                }
            }))
        else:
            self.finish(json.dumps({
                'error': {
                    'code': status_code,
                    'message': self._reason,
                }
            }))

class ParamHandler(BaseHandler):

    def __init__(self, app, request, **kwargs):
        self.root = kwargs.pop('root', None)
        super().__init__(app, request, **kwargs)

    @classmethod
    def serialize(cls, parameterized, parameters):
        values = {p: getattr(parameterized, p) for p in parameters}
        return parameterized.param.serialize_parameters(values)

    @classmethod
    def deserialize(cls, parameterized, parameters):
        for p in parameters:
            if p not in parameterized.param:
                reason = f"'{p}' query parameter not recognized."
                raise HTTPError(reason=reason, status_code=400)
        return {p: parameterized.param.deserialize_value(p, v)
                for p, v in parameters.items()}

    async def get(self):
        path = self.request.path
        endpoint = path[path.index(self.root)+len(self.root):]
        parameterized, parameters, _ = state._rest_endpoints.get(
            endpoint, (None, None, None)
        )
        if not parameterized:
            return
        args = parse_qs(self.request.query)
        params = self.deserialize(parameterized[0], args)
        parameterized[0].param.update(**params)
        self.set_header('Content-Type', 'application/json')
        self.write(self.serialize(parameterized[0], parameters))


def build_tranquilize_application(files):
    from tranquilizer.handler import NotebookHandler, ScriptHandler
    from tranquilizer.main import UnsupportedFileType, make_app

    functions = []
    for filename in files:
        extension = filename.split('.')[-1]
        if extension == 'py':
            source = ScriptHandler(filename)
        elif extension == 'ipynb':
            try:
                import nbconvert  # noqa
            except ImportError as e: # pragma no cover
                raise ImportError("Please install nbconvert to serve Jupyter Notebooks.") from e

            source = NotebookHandler(filename)
        else:
            raise UnsupportedFileType(f'{filename} is not a script (.py) or notebook (.ipynb)')
        functions.extend(source.tranquilized_functions)
    return make_app(functions, 'Panel REST API', prefix='rest/')


def tranquilizer_rest_provider(files, endpoint):
    """
    Returns a Tranquilizer based REST API. Builds the API by evaluating
    the scripts and notebooks being served and finding all tranquilized
    functions inside them.

    Parameters
    ----------
    files: list(str)
      A list of paths being served
    endpoint: str
      The endpoint to serve the REST API on

    Returns
    -------
    A Tornado routing pattern containing the route and handler
    """
    app = build_tranquilize_application(files)
    tr = WSGIContainer(app)
    return [(rf"^/{endpoint}/.*", web.FallbackHandler, dict(fallback=tr))]


def param_rest_provider(files, endpoint):
    """
    Returns a Param based REST API given the scripts or notebooks
    containing the tranquilized functions.

    Parameters
    ----------
    files: list(str)
      A list of paths being served
    endpoint: str
      The endpoint to serve the REST API on

    Returns
    -------
    A Tornado routing pattern containing the route and handler
    """
    for filename in files:
        extension = filename.split('.')[-1]
        if extension == 'py':
            try:
                run_path(filename)
            except Exception:
                param.main.param.warning("Could not run app script on REST server startup.")
        elif extension == 'ipynb':
            try:
                import nbconvert  # noqa
            except ImportError:
                raise ImportError("Please install nbconvert to serve Jupyter Notebooks.") from None
            from nbconvert import ScriptExporter
            exporter = ScriptExporter()
            source, _ = exporter.from_filename(filename)
            source_dir = os.path.dirname(filename)
            with tempfile.NamedTemporaryFile(mode='w', dir=source_dir, delete=True) as tmp:
                tmp.write(source)
                tmp.flush()
                try:
                    run_path(tmp.name, init_globals={'get_ipython': MagicMock()})
                except Exception:
                    param.main.param.warning("Could not run app notebook on REST server startup.")
        else:
            raise ValueError(f'{filename} is not a script (.py) or notebook (.ipynb)')

    if endpoint and not endpoint.endswith('/'):
        endpoint += '/'
    return [((rf"^/{endpoint}.*" if endpoint else r"^.*"), ParamHandler, dict(root=endpoint))]


REST_PROVIDERS = {
    'tranquilizer': tranquilizer_rest_provider,
    'param': param_rest_provider
}

# Populate REST Providers from external extensions
for entry_point in entry_points_for('panel.io.rest'):
    REST_PROVIDERS[entry_point.name] = entry_point.load()
