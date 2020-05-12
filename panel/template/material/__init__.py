"""
Material template based on the material web components library.
"""
import pathlib

import param

from ...config import config
from ...layout import Row, Column, HSpacer, Spacer, ListLike, Card
from ...pane import HTML
from ..base import BasicTemplate
from ..theme import DefaultTheme



class MaterialTemplate(BasicTemplate):
    """
    MaterialTemplate is built on top of Material web components.
    """

    _css = pathlib.Path(__file__).parent / 'material.css'

    _template = pathlib.Path(__file__).parent / 'material.html'

    _modifiers = {
        Card: {
            'title_css_classes': ['mdc-card-title'],
            'css_classes': ['mdc-card'],
            'header_css_classes': ['mdc-card__primary-action'],
            'button_css_classes': ['mdc-button', 'mdc-card-button']
        },
    }

    def __init__(self, **params):
        super(MaterialTemplate, self).__init__(**params)
        self._snackbar_trigger = HTML()
        self._render_items['snackbar_trigger'] = (self._snackbar_trigger, [])

    def toast(self, msg):
        script = """
        <script>
        var snackbar = new mdc.snackbar.MDCSnackbar(document.querySelector('.mdc-snackbar'));
        snackbar.labelText = '{msg}'
        snackbar.open()
        </script>
        """.format(msg=msg)
        self._snackbar_trigger.object = script
        self._snackbar_trigger.object = ''


class MaterialDefaultTheme(DefaultTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'default.css')

    _template = MaterialTemplate
