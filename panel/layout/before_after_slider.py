"""
The BeforeAfterSlider layout enables you to quickly compare two panels
"""

import param

from ..reactive import ReactiveHTML
from .base import ListLike


class BeforeAfterSlider(ListLike, ReactiveHTML):
    """
    The BeforeAfterSlider layout enables you to quickly compare two
    panels layed out on top of each other with a part of the *before*
    panel shown on one side of a slider and a part of the
    *after* panel shown on the other side."""

    objects = param.List(default=[], bounds=(0, 2), doc="""
        The list of child objects that make up the layout.""", precedence=-1)

    slider_width = param.Integer(default=12, bounds=(0, 25), doc="""
        The width of the slider in pixels""")

    slider_color = param.Color(default="silver", doc="""
        The color of the slider""")

    value = param.Integer(50, bounds=(0, 100), doc="""
        The percentage of the *after* panel to show.""")

    _before = param.Parameter()

    _after = param.Parameter()

    _template = """
    <div id="container" class="before-after-container">
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
          set_size(container, model)
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
           after.style.width = `calc(${data.value}% + 5px)`
           self.adjustSlider()
        """,
        'slider_width': """
           self.adjustSlider()
        """,
        'adjustSlider': """
           halfWidth = parseInt(data.slider_width/2)
           slider.style.marginLeft = `calc(${data.value}% + 5px - ${halfWidth}px)`
        """
    }

    def __init__(self, *objects, **params):
        if 'objects' in params and objects:
            raise ValueError(
                "Either supply objects as an positional argument or "
                "as a keyword argument, not both."
            )
        objects = params.pop('objects', objects)
        super().__init__(objects=list(objects), **params)

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
