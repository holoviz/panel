import bokeh.core.properties as bp

from bokeh.model import DataModel

from ..config import config
from ..io.resources import bundled_files
from ..util import classproperty
from .layout import HTMLBox


class ReactiveESM(HTMLBox):

    children = bp.List(bp.String)

    data = bp.Instance(DataModel)

    dev = bp.Bool(False)

    esm = bp.String()

    importmap = bp.Dict(bp.String, bp.Dict(bp.String, bp.String))

    __javascript_modules_raw__ = [
        f"{config.npm_cdn}/es-module-shims@^1.10.0/dist/es-module-shims.min.js"
    ]

    @classproperty
    def __javascript_modules__(cls):
        return bundled_files(cls, 'javascript_modules')


class ReactComponent(ReactiveESM):
    """
    Renders jsx/tsx based ESM bundles using React.
    """

    react_version = bp.String('18.2.0')


class PreactComponent(ReactiveESM):
    """
    Renders htm based output using Preact.
    """

class AnyWidgetComponent(ReactComponent):
    """
    Renders AnyWidget esm definitions by adding a compatibility layer.
    """
