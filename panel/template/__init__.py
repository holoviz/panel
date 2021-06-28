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
    'fast'      : FastListTemplate,
    'fast-list' : FastListTemplate,
    'material'  : MaterialTemplate,
    'golden'    : GoldenTemplate,
    'vanilla'   : VanillaTemplate
}

_config.param.template.names = templates
_config.param.template.objects = list(templates)
