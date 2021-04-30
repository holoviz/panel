from ..config import _config
from .base import Template, BaseTemplate # noqa
from .bootstrap import BootstrapTemplate # noqa
from .fast import FastListTemplate, FastGridTemplate # noqa
from .material import MaterialTemplate # noqa
from .theme import DarkTheme, DefaultTheme # noqa
from .golden import GoldenTemplate # noqa
from .react import ReactTemplate # noqa
from .vanilla import VanillaTemplate # noqa

templates = {
    'bootstrap' : BootstrapTemplate,
    'fast-list' : FastListTemplate,
    'fast-grid' : FastGridTemplate,
    'material'  : MaterialTemplate,
    'golden'    : GoldenTemplate,
    'react-grid': ReactTemplate,
    'vanilla'   : VanillaTemplate
}

_config.param.template.names = templates
_config.param.template.objects = list(templates)
