from ..config import _config
from ..theme import DarkTheme, DefaultTheme  # noqa
from .base import BaseTemplate, Template  # noqa
from .bootstrap import BootstrapTemplate  # noqa
from .fast import FastGridTemplate, FastListTemplate  # noqa
from .golden import GoldenTemplate  # noqa
from .material import MaterialTemplate  # noqa
from .react import ReactTemplate  # noqa
from .slides import SlidesTemplate  # noqa
from .vanilla import VanillaTemplate  # noqa

templates = {
    'bootstrap' : BootstrapTemplate,
    'fast'      : FastListTemplate,
    'fast-list' : FastListTemplate,
    'material'  : MaterialTemplate,
    'golden'    : GoldenTemplate,
    'slides'    : SlidesTemplate,
    'vanilla'   : VanillaTemplate
}

_config.param.template.objects = list(templates)
_config.param.template.names = templates

__all__ = [
    "BaseTemplate",
    "BootstrapTemplate",
    "DarkTheme",
    "DefaultTheme",
    "FastGridTemplate",
    "FastListTemplate",
    "GoldenTemplate",
    "MaterialTemplate",
    "ReactTemplate",
    "SlidesTemplate",
    "Template",
    "VanillaTemplate",
]
