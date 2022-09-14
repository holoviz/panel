from tornado import web

from .document import _cleanup_doc
from .state import set_curdoc, state


class LivenessHandler(web.RequestHandler):

    def initialize(self, applications):
        self.applications = applications

    async def get(self):
        endpoint = self.get_argument("endpoint", default=None)
        self.set_header('Content-Type', 'application/json')
        if endpoint is not None and endpoint not in self.applications:
            raise web.HTTPError(400, f"Endpoint {endpoint!r} does not exist.")
        elif endpoint is None:
            self.write({self.request.path: True})
            return

        app = self.applications[endpoint]
        try:
            doc = app.create_document()
            with set_curdoc(doc):
                state._on_load(None)
            _cleanup_doc(doc)
            self.write({endpoint: True})
        except Exception as e:
            raise web.HTTPError(
                500, f"Endpoint {endpoint!r} could not be served. Application raised error: {e}"
            )
