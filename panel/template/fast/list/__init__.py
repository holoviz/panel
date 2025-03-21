"""
The FastListTemplate provides a list layout based on similar to the
Panel VanillaTemplate but in the Fast.design style and enabling the
use of Fast components.
"""
import pathlib

import param

from ....layout import ListLike
from ....pane import HoloViews
from ..base import FastBaseTemplate


class FastListTemplate(FastBaseTemplate):
    """
    The `FastListTemplate` is a list based Template with a header, sidebar, main, secondary (right) sidebar and modal area.
    It is based on the fast.design style and works well in both default (light) and dark mode.

    Reference: https://panel.holoviz.org/reference/templates/FastListTemplate.html

    :Example:

    >>> pn.template.FastListTemplate(
    ...     site="Panel", title="FastListTemplate", accent="#A01346",
    ...     sidebar=[pn.pane.Markdown("## Settings"), some_slider],
    ...     main=[some_python_object]
    ... ).servable()

    Some *accent* colors that work well are #A01346 (Fast), #00A170 (Mint), #DAA520 (Golden Rod),
    #2F4F4F (Dark Slate Grey), #F08080 (Light Coral) and #4099da (Summer Sky).

    You can also use the `FastListTemplate` as shown below

    >>> pn.extension(..., template="fast")
    >>> pn.state.template.param.update(site="Panel", title="FastListTemplate", accent="#A01346")
    >>> pn.pane.Markdown("## Settings").servable(target="sidebar")
    >>> some_slider = pn.widgets.IntSlider(...).servable(target="sidebar")
    >>> ...
    >>> pn.panel(some_python_object).servable(target="main")

    This api is great for more exploratory use cases.

    Please note the `FastListTemplate` cannot display in a notebook output cell.
    """

    collapsed_right_sidebar = param.Selector(default=False, constant=True, doc="""
       Whether the secondary sidebar on the right (if present) is initially collapsed.""")

    right_sidebar = param.ClassSelector(class_=ListLike, constant=True, doc="""
        A list-like container which populates a secondary sidebar (on the right).""")

    right_sidebar_footer = param.String("", doc="""
        A HTML string appended to a secondary sidebar (right sidebar).""")

    right_sidebar_width = param.Integer(default=330, doc="""
        The width of the secondary sidebar (right sidebar) in pixels. Default is 330.""")

    _css = FastBaseTemplate._css + [
        pathlib.Path(__file__).parent / "fast_list_template.css"
    ]

    _template = pathlib.Path(__file__).parent / "fast_list_template.html"

    def __init__(self, **params):
        if "right_sidebar" not in params:
            params["right_sidebar"] = ListLike()
        else:
            params["right_sidebar"] = self._get_params(params["right_sidebar"], self.param.right_sidebar.class_)
        super().__init__(**params)
        self.right_sidebar.param.watch(self._update_right_sidebar_render_items, ['objects'])
        self.right_sidebar.param.trigger('objects')

    def _update_vars(self):
        super()._update_vars()
        self._render_variables["right_sidebar_width"] = self.right_sidebar_width
        self._render_variables["right_sidebar_footer"] = self.right_sidebar_footer
        self._render_variables['collapsed_right_sidebar'] = self.collapsed_right_sidebar

    def _update_right_sidebar_render_items(self, event: param.parameterized.Event) -> None:
        if event.obj is self.right_sidebar:
            tag = 'right_nav'

        old = event.old if isinstance(event.old, list) else list(event.old.values())
        for obj in old:
            ref = f'{tag}-{str(id(obj))}'
            if ref in self._render_items:
                del self._render_items[ref]

        new = event.new if isinstance(event.new, list) else event.new.values()
        if self._design.theme.bokeh_theme:
            for o in new:
                if o in old:
                    continue
                for hvpane in o.select(HoloViews):
                    hvpane.theme = self._design.theme.bokeh_theme

        labels = {}
        for obj in new:
            ref = f'{tag}-{str(id(obj))}'
            if obj.name.startswith(type(obj).__name__):
                labels[ref] = 'Content'
            else:
                labels[ref] = obj.name
            self._render_items[ref] = (obj, [tag])
        tags = [tags for _, tags in self._render_items.values()]
        self._render_variables['right_nav'] = any('right_nav' in ts for ts in tags)
