"""
The Fade layout enables you to quickly compare multiple panels
"""
from __future__ import annotations

from typing import ClassVar, List

import param

from ..io.resources import CDN_DIST
from ..reactive import ReactiveHTML
from .base import ListLike


class Fade(ListLike, ReactiveHTML):
    """
    The Fade layout enables you to quickly compare multiple objects;
    laid on top of each other with a slider to fade between them.
    For example, if there are two objects, the first panel will be
    fully opaque when the slider is at 0%, the second panel will be
    fully opaque when the slider is at 100%, and both objects will be
    half opaque when the slider is at 50%.
    This can also support more than two objects and will gradually
    fade between object 0 to object 1 to object 2.
    """

    objects = param.List(
        default=[],
        doc="The list of child objects that make up the layout.",
        precedence=-1,
    )

    slider_width = param.Integer(
        default=25,
        bounds=(0, 100),
        doc="The width of the slider in pixels",
    )

    slider_color = param.Color(
        default="black",
        doc="The color of the slider",
    )

    value = param.Integer(
        default=0,
        bounds=(0, 100),
        doc="The percentage value of the slider.",
    )

    _objects = param.List(default=[])

    _direction: ClassVar[str | None] = "vertical"

    _template = """
    <div id="fade-container" class="fade-container">
        {% for obj in _objects %}
        <div id="object-{{ loop.index0 }}" class="outer" style="overflow: hidden;">
            <div id="object-inner-{{ loop.index0 }}" class="inner">${obj}</div>
        </div>
        {% endfor %}
        <div id="slider" class="slider" onmousedown="${script('drag')}"
            style="background: ${slider_color}; width: ${slider_width}px;">
        </div>
        <div class="slider-line"></div>
    </div>
    """

    _scripts = {
        "render": """
            data.value = 0;
            self.adjustSlider()
        """,
        "after_layout": """
            self.value()
        """,
        "drag": """
            function endDrag() {
                document.removeEventListener('mouseup', endDrag);
                document.removeEventListener('mousemove', handleDrag);
            }
            function handleDrag(e) {
                e = e || window.event;
                e.preventDefault();
                current = e.clientX
                start = view.el.getBoundingClientRect().left
                value = parseInt(((current-start)/ fade_container.clientWidth)*100)
                data.value = Math.max(0, Math.min(value, 100))
            }
            let e = event || window.event;
            e.preventDefault();
            document.addEventListener('mouseup', endDrag);
            document.addEventListener('mousemove', handleDrag);
        """,
        "value": """
            objects = fade_container.getElementsByClassName('outer');
            const numObjects = objects.length;
            const sliderValue = data.value / 100; // Scale data.value to range 0-1

            const opacityStep = 1 / (numObjects - 1);
            const nearestObjectIndex = Math.floor(sliderValue / opacityStep);
            const remainder = sliderValue % opacityStep;

            let opacity;
            for (let i = 0; i < numObjects; i++) {
                if (i === nearestObjectIndex) {
                    opacity = 1 - remainder / opacityStep;
                } else if (i === nearestObjectIndex + 1) {
                    opacity = remainder / opacityStep;
                } else {
                    opacity = (nearestObjectIndex < i && i < nearestObjectIndex + 1) ? 1 : 0;
                }
                console.log(opacity, i);
                objects[i].style.opacity = opacity;
            }
            self.adjustSlider();
        """,
        "slider_width": "self.adjustSlider()",
        "adjustSlider": """
            halfWidth = parseInt(data.slider_width/2)
            slider.style.marginLeft = `calc(${data.value}% - ${halfWidth}px)`
        """,
    }

    _stylesheets: ClassVar[List[str]] = [f"{CDN_DIST}css/fade.css"]

    def __init__(self, *objects, **params):
        if "objects" in params and objects:
            raise ValueError(
                "Either supply objects as a positional argument or "
                "as a keyword argument, not both."
            )
        from ..pane.base import panel

        objects = params.pop("objects", objects)
        if not objects:
            objects = [None, None]
        super().__init__(objects=[panel(obj) for obj in objects], **params)

    @param.depends("objects", watch=True, on_init=True)
    def _update_layout(self):
        for i, obj in enumerate(self.objects):
            if i < len(self._objects):
                self._objects[i] = obj
            else:
                self._objects.append(obj)

    def select(self, selector=None):
        """
        Iterates over the Viewable and any potential children in the
        applying the Selector.

        Arguments
        ---------
        selector: type or callable or None
          The selector allows selecting a subset of Viewables by
          declaring a type or callable function to filter by.

        Returns
        -------
        viewables: list(Viewable)
        """
        objects = super().select(selector)
        for obj in self._objects:
            objects += obj.select(selector)
        return objects
