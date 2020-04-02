import json

from ast import literal_eval
from urllib.parse import parse_qs

import param

from tornado import web

from .state import state


class HTTPError(web.HTTPError):

    pass


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

    @classmethod
    def serialize(cls, parameterized, parameters):
        return {p: getattr(parameterized, p) for p in parameters}

    @classmethod
    def deserialize(cls, parameterized, parameters):
        params = {}
        for p, values in parameters.items():
            if p not in parameterized.param:
                raise HTTPError(reason="%s query parameter not recognized." % p,
                                status_code=400)
            parameter = parameterized.param[p]
            value = values[0]
            if not isinstance(parameter, param.String):
                value = literal_eval(value)
            params[p] = value
        return params
        
    def get(self):
        endpoint = self.request.path
        parameterized, parameters, _ = state._rest_endpoints.get(
            endpoint, (None, None, None)
        )
        if not parameterized:
            return
        args = parse_qs(self.request.query)
        params = self.deserialize(parameterized[0], args)
        parameterized[0].param.set_param(**params)
        self.set_header('Content-Type', 'application/json')
        self.write(self.serialize(parameterized[0], parameters))


def build_tranquilize_application(files, argv):
    from tranquilizer.handler import ScriptHandler, NotebookHandler
    from tranquilizer.main import make_app, UnsupportedFileType

    functions = []
    for filename in files:
        extension = filename.split('.')[-1]
        if extension == 'py':
            source = ScriptHandler(filename)
        elif extension == 'ipynb':
            try:
                import nbconvert # noqa
            except ImportError as e: # pragma no cover
                raise ImportError("Please install nbconvert to serve Jupyter Notebooks.") from e

            source = NotebookHandler(filename)
        else:
            raise UnsupportedFileType('{} is not a script (.py) or notebook (.ipynb)'.format(filename))
        functions.extend(source.tranquilized_functions)
    return make_app(functions, 'Panel REST API', prefix='rest/')
