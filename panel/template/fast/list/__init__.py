"""
The FastListTemplate provides a list layout based on similar to the
Panel VanillaTemplate but in the Fast.design style and enabling the
use of Fast components.
"""
import pathlib

from ..base import FastBaseTemplate


class FastListTemplate(FastBaseTemplate):
    """
    The `FastListTemplate` is a list based Template with a header, sidebar and main area. It is
    based on the fast.design style and works well in both default (light) and dark mode.

    Reference: https://panel.holoviz.org/reference/templates/FastListTemplate.html

    Example:

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

    _css = FastBaseTemplate._css + [
        pathlib.Path(__file__).parent / "fast_list_template.css"
    ]

    _template = pathlib.Path(__file__).parent / "fast_list_template.html"
