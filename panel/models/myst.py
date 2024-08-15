from ..config import config
from ..io.resources import bundled_files
from ..util import classproperty
from .markup import HTML


class MyST(HTML):
    """
    A bokeh model to render MyST markdown on the client side
    """

    __javascript_module_exports__ = ['* as mystjs']

    __javascript_modules_raw__ = [
        f"{config.npm_cdn}/mystjs@0.0.15/+esm"
    ]

    @classproperty
    def __javascript_modules__(cls):
        return bundled_files(cls, 'javascript_modules')
