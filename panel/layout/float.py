from __future__ import annotations

from typing import ClassVar

import param

from ..config import config as pn_config
from ..io.resources import CDN_DIST, bundled_files
from ..reactive import ReactiveHTML
from ..util import classproperty
from .base import ListLike

POSITIONS = [
    'center',
    'left-top',
    'center-top',
    'right-top',
    'right-center',
    'right-bottom',
    'center-bottom',
    'left-bottom',
    'left-center',
]

STATUS = [
    "normalized",
    "maximized",
    "minimized",
    "smallified",
    "smallifiedmax",
    "closed"
]

class FloatPanel(ListLike, ReactiveHTML):
    """
    Float provides a floating panel layout.

    Reference: https://panel.holoviz.org/reference/layouts/FloatPanel.html

    :Example:

    >>> import panel as pn
    >>> pn.extension("floatpanel")
    >>> pn.layout.FloatPanel("**I can float**!", position="center", width=300).servable()
    """

    config = param.Dict({}, doc="""
       Additional jsPanel configuration with precedence over
       parameter values.""")

    contained = param.Boolean(default=True, doc="""
       Whether the component is contained within parent container
       or completely free floating.""")

    position = param.Selector(default='right-top', objects=POSITIONS, doc="""
       The initial position if the container is free-floating.""")

    offsetx = param.Integer(default=None, bounds=(0, None), doc="""
       Horizontal offset in pixels.""")

    offsety = param.Integer(default=None, bounds=(0, None), doc="""
       Vertical offset in pixels.""")

    theme = param.String(default="primary", doc="""
        The theme which can be one of:

        - Built-ins: 'default', 'primary', 'secondary', 'info',
          'success', 'warning', 'danger', 'light', 'dark' and 'none'
        - HEX, RGB and HSL color values like '#123456' Any
          standardized color name like 'forestgreen' and color names
          from the Material Design Color System like 'purple900'
        - Additionally a theme string may include one of the modifiers
          'filled', 'filledlight', 'filleddark' or 'fillcolor'
          separated from the theme color by a space like 'primary""")

    status = param.Selector(default="normalized", objects=STATUS, doc="""
        The current status of the panel.""")

    _extension_name = 'floatpanel'

    _template = """
    <div id="float" class="bk-root" style="padding:8px;padding-right:30px">
      {% for obj in objects %}
      <div id="flex-item">${obj}</div>
      {% endfor %}
    </div>
    """

    _rename = {'loading': None}

    _scripts = {
        "render": """
        if (state.panel) {
          view.run_script('close')
        }
        var config = {
          headerTitle: data.name,
          content: float,
          theme: data.theme,
          id: 'jsPanel'+data.id,
          position: view.run_script('get_position'),
          contentSize: `${model.width} ${model.height}`,
          onstatuschange: function() {
            data.status = this.status
          },
          onbeforeclose: function() {
           data.status = 'closed'
           return true
          },
        }
        if (data.contained) {
          config.container = view.container
        }
        config = {...config, ...data.config}
        state.panel = jsPanel.create(config);
        if (data.status !== 'normalized') {
          view.run_script('status')
        }
        state.resizeHandler = (event) => {
          if (event.panel === state.panel) {
            view.invalidate_layout()
          }
        }
        document.addEventListener('jspanelresizestop', state.resizeHandler, false)
        """,
        "name": "state.panel.setHeaderTitle(data.name)",
        "status": """
        var action = data.status.replace('ied', 'y').replace('d', '')
        if (action === 'close') {
          state.closed = true
        } else if (state.closed) {
          view.run_script('close')
          return
        }
        state.panel[action]()
        """,
        "close": "try { state.panel.close() } catch {}",
        "get_position": """
        return {
            at: data.position,
            my: data.position,
            offsetX: data.offsetx,
            offsetY: data.offsety,
        }
        """,
        "reposition": """
        if (data.contained) {
          view.run_script('contained')
          return
        }
        state.panel.reposition(view.run_script('get_position'));
        """,
        "contained": "delete state.panel; view.invalidate_render();",
        "theme": "state.panel.setTheme(data.theme)",
        "remove": """
        document.removeEventListener('jspanelresizestop', state.resizeHandler, false);
        view.run_script('close');
        state.panel = undefined;
        """,
        "offsetx": "view.run_script('reposition')",
        "offsety": "view.run_script('reposition')",
        "position": "if (!data.contained) { view.run_script('reposition') }",
    }

    __css_raw__ = [f"{pn_config.npm_cdn}/jspanel4@4.12.0/dist/jspanel.css"]

    __javascript_raw__ = [
        f"{pn_config.npm_cdn}/jspanel4@4.12.0/dist/jspanel.js",
        f"{pn_config.npm_cdn}/jspanel4@4.12.0/dist/extensions/modal/jspanel.modal.js",
        f"{pn_config.npm_cdn}/jspanel4@4.12.0/dist/extensions/tooltip/jspanel.tooltip.js",
        f"{pn_config.npm_cdn}/jspanel4@4.12.0/dist/extensions/hint/jspanel.hint.js",
        f"{pn_config.npm_cdn}/jspanel4@4.12.0/dist/extensions/layout/jspanel.layout.js",
        f"{pn_config.npm_cdn}/jspanel4@4.12.0/dist/extensions/contextmenu/jspanel.contextmenu.js",
        f"{pn_config.npm_cdn}/jspanel4@4.12.0/dist/extensions/dock/jspanel.dock.js",
    ]

    __js_require__ = {
        'paths': {
            'jspanel': f"{pn_config.npm_cdn}/jspanel4@4.12.0/dist/jspanel",
            'jspanel-modal': f"{pn_config.npm_cdn}/jspanel4@4.12.0/dist/extensions/modal/jspanel.modal",
            'jspanel-tooltip': f"{pn_config.npm_cdn}/jspanel4@4.12.0/dist/extensions/tooltip/jspanel.tooltip",
            'jspanel-hint': f"{pn_config.npm_cdn}/jspanel4@4.12.0/dist/extensions/hint/jspanel.hint",
            'jspanel-layout': f"{pn_config.npm_cdn}/jspanel4@4.12.0/dist/extensions/layout/jspanel.layout",
            'jspanel-contextmenu': f"{pn_config.npm_cdn}/jspanel4@4.12.0/dist/extensions/contextmenu/jspanel.contextmenu",
            'jspanel-dock': f"{pn_config.npm_cdn}/jspanel4@4.12.0/dist/extensions/dock/jspanel.dock",
        },
        'exports': {
            'jspanel': 'jsPanel'
        },
        'shim': {
            'jspanel': {
                'exports': 'jsPanel'
            }
        }
    }

    _stylesheets: ClassVar[list[str]] = [
        f'{CDN_DIST}css/floatpanel.css'
    ]

    @classproperty
    def __js_skip__(cls):
        return {
            'jsPanel': cls.__javascript__,
        }

    @classproperty
    def __javascript__(cls):
        return bundled_files(cls)

    @classproperty
    def __css__(cls):
        return bundled_files(cls, 'css')

    def __init__(self, *objects, name='', **params):
        super().__init__(objects=list(objects), name=name, **params)

    def select(self, selector=None):
        """
        Iterates over the Viewable and any potential children in the
        applying the Selector.

        Parameters
        ----------
        selector: type or callable or None
          The selector allows selecting a subset of Viewables by
          declaring a type or callable function to filter by.

        Returns
        -------
        viewables: list(Viewable)
        """
        objects = super().select(selector)
        for obj in self:
            objects += obj.select(selector)
        return objects
