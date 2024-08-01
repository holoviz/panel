from bokeh.models import Tabs as BkTabs


class Tabs(BkTabs):
    """
    Subclass of bokeh tabs with handling to ensure z-index correctness.
    """
