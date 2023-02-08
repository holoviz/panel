"""
Bootstrap template based on the bootstrap.css library.
"""
from __future__ import annotations

import pathlib

from typing import ClassVar, Dict, List

import param

from ...theme import Themer
from ...theme.bootstrap import Bootstrap
from ..base import BasicTemplate, TemplateActions

_ROOT = pathlib.Path(__file__).parent


class BootstrapTemplateActions(TemplateActions):

    _scripts: ClassVar[Dict[str, List[str] | str]] = {
        'render': "state.modal = new bootstrap.Modal(document.getElementById('pn-Modal'))",
        'open_modal': "state.modal.show()",
        'close_modal': "state.modal.hide()",
    }


class BootstrapTemplate(BasicTemplate):
    """
    BootstrapTemplate
    """

    sidebar_width = param.Integer(350, doc="""
        The width of the sidebar in pixels. Default is 350.""")

    themer = param.ClassSelector(class_=Themer, default=Bootstrap, constant=True,
                                 is_instance=False, instantiate=False, doc="""
        A Themer applies a specific design system to a template.""")

    _actions = param.ClassSelector(default=BootstrapTemplateActions(), class_=TemplateActions)

    _css = [_ROOT / "bootstrap.css"]

    _template = _ROOT / 'bootstrap.html'

    def _update_vars(self, *args) -> None:
        super()._update_vars(*args)
        themer = self.themer(theme=self.theme)
        self._render_variables['html_attrs'] = f'data-bs-theme="{themer.theme._bs_theme}"'
