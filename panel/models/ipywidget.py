from bokeh.core.properties import Any
from bokeh.models.layouts import HTMLBox


class IPyWidget(HTMLBox):

    bundle = Any()

    def __init__(self, widget, **kwargs):
        from ipywidgets import Widget, embed
        super().__init__(**kwargs)
        spec = widget.get_view_spec()
        state = Widget.get_manager_state(widgets=[])
        state["state"] = embed.dependency_state([widget], drop_defaults=True)
        self.bundle = dict(spec=spec, state=state)
