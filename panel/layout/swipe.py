"""
The Swipe layout enables you to quickly compare two panels
"""
from __future__ import annotations

from typing import ClassVar

import param

from ..io.resources import CDN_DIST
from ..reactive import ReactiveHTML
from .base import ListLike


class Swipe(ListLike, ReactiveHTML):
    """
    The Swipe layout enables you to quickly compare two panels laid
    out on top of each other with a part of the *before* panel shown
    on one side of a slider and a part of the *after* panel shown on
    the other side.
    """

    objects = param.List(default=[], bounds=(0, 2), doc="""
        The list of child objects that make up the layout.""", precedence=-1)

    slider_width = param.Integer(default=5, bounds=(0, 25), doc="""
        The width of the slider in pixels""")

    slider_color = param.Color(default="black", doc="""
        The color of the slider""")

    value = param.Integer(default=50, bounds=(0, 100), doc="""
        The percentage of the *after* panel to show.""")

    _before = param.Parameter()

    _after = param.Parameter()

    _direction: ClassVar[str | None] = 'vertical'

    _template = """
    <div id="container" class="swipe-container">
      <div id="before" class="outer">
        <div id="before-inner" class="inner">${_before}</div>
      </div>
      <div id="after" class="outer" style="overflow: hidden;">
        <div id="after-inner" class="inner">${_after}</div>
      </div>
      <div id="slider" class="slider" onmousedown="${script('drag')}"
           style="background: ${slider_color}; width: ${slider_width}px;">
      </div>
    </div>
    """

    _scripts = {
        'render': """
          self.adjustSlider()
        """,
        'after_layout': """
          self.value()
        """,
        'drag': """
          function endDrag() {
             document.removeEventListener('mouseup', endDrag);
             document.removeEventListener('mousemove', handleDrag);
           }
           function handleDrag(e) {
             e = e || window.event;
             e.preventDefault();
             current = e.clientX
             start = view.el.getBoundingClientRect().left
             value = parseInt(((current-start)/ container.clientWidth)*100)
             data.value = Math.max(0, Math.min(value, 100))
           }
           let e = event || window.event;
           e.preventDefault();
           document.addEventListener('mouseup', endDrag);
           document.addEventListener('mousemove', handleDrag);
        """,
        'value': """
           before.style.clipPath = `polygon(0% 0%, calc(${data.value}% + 5px) 0%, calc(${data.value}% + 5px) 100%, 0% 100%)`
           after.style.clipPath = `polygon(calc(${data.value}% + 5px) 0%, 100% 0%, 100% 100%, calc(${data.value}% + 5px) 100%)`
           self.adjustSlider()
        """,
        'slider_width': "self.adjustSlider()",
        'adjustSlider': """
           halfWidth = parseInt(data.slider_width/2)
           slider.style.marginLeft = `calc(${data.value}% + 5px - ${halfWidth}px)`
        """
    }

    _stylesheets: ClassVar[list[str]] = [
        f'{CDN_DIST}css/swipe.css'
    ]

    def __init__(self, *objects, **params):
        if 'objects' in params and objects:
            raise ValueError(
                "Either supply objects as an positional argument or "
                "as a keyword argument, not both."
            )
        from ..pane.base import panel
        objects = params.pop('objects', objects)
        if not objects:
            objects = [None, None]
        super().__init__(objects=[panel(obj) for obj in objects], **params)

    @param.depends('objects', watch=True, on_init=True)
    def _update_layout(self):
        self._before = self.before
        self._after = self.after

    @property
    def before(self):
        return self[0] if len(self) else None

    @before.setter
    def before(self, before):
        self[0] = before

    @property
    def after(self):
        return self[1] if len(self) > 1 else None

    @after.setter
    def after(self, after):
        self[1] = after

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
