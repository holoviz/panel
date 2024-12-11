from ..config import config
from ..io.resources import bundled_files
from ..util import classproperty
from .markup import HTML


class MyST(HTML):
    """
    A bokeh model to render MyST markdown on the client side
    """

    __javascript_module_exports__ = ['* as mystparser', '* as myst2html']

    __javascript_modules_raw__ = [
        f"{config.npm_cdn}/myst-parser@1.5.3/+esm",
        f"{config.npm_cdn}/myst-to-html@1.5.3/+esm"
    ]

    @classproperty
    def __javascript_modules__(cls):
        return bundled_files(cls, 'javascript_modules')

    __javascript_raw__ = [
        'https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/highlight.min.js'
    ]

    @classproperty
    def __javascript__(cls):
        return bundled_files(cls)

    __css_raw__ = [
        'https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/github-dark.min.css'
    ]

    @classproperty
    def __css__(cls):
        return bundled_files(cls, 'css')
