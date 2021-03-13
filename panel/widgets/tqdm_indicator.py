# I did not put it into the indicators.py file yet as it raises errors due to circular imports I
# believe
import panel as pn
import param
from tqdm.auto import tqdm as _tqdm


EMPTY_TEXT = " " # Hack: If set to None or "" the height of the text_pane is too little

MARGIN = {
    "text_pane": {
        "column": (5, 10, 0, 10), "row": (0, 10, 0, 10)
    },
    "progress_indicator": {
        "column": (0, 10, 5, 10), "row": (12, 10, 0, 10)
    }
}

# I cannot have it inherit from pn.indicators.BaseIndicator as that raises an exception
class TQDMProgress(pn.viewable.Viewer):
    text = param.String(default=EMPTY_TEXT)
    max = param.Integer(default=100, doc="The maximum value of the progress bar.")
    value = param.Integer(default=0, bounds=(0, None), doc="""
        The current value of the progress bar. If set to None the progress
        bar will be indeterminate and animate depending on the active
        parameter.""")
    write_to_console = param.Boolean(default=False, )

    progress_indicator = param.ClassSelector(class_=pn.indicators.Progress, doc="""
        The Progress indicator to display to. Default is a pn.indicators.Progress
    """, precedence=-1)
    text_pane = param.ClassSelector(class_=pn.pane.Str, doc="""
        The pane to display the text to. Default is a pn.pane.Str
    """, precedence=-1)
    panel = param.ClassSelector(class_=(pn.Column, pn.Row), doc="""
        The panel to laying out the text_pane and progress_indicator. Default is a Column.
    """, precedence=-1)

    tqdm = param.Parameter(precedence=-1)

    def __init__(self, layout="column", **params):
        if not "text_pane" in params:
            params["text_pane"]=pn.pane.Str(self.text, sizing_mode="stretch_width", margin=MARGIN["text_pane"][layout])
        if not "progress_widget" in params:
            params["progress_indicator"]=pn.widgets.Progress(active=False, sizing_mode="stretch_width", margin=MARGIN["progress_indicator"][layout])
        if not "tqdm" in params:
            params["tqdm"]=self._get_tqdm()

        layout_params = {}
        for key in params.copy():
            if hasattr(pn.layout.base.ListPanel,key):
                layout_params[key]=params.pop(key)

        super().__init__(**params)

        self.progress_indicator.max = self.max
        self.progress_indicator.value = self.value
        self.text_pane = self.text_pane

        if layout=="row":
            self.panel = pn.Row(self.progress_indicator, self.text_pane, **layout_params)
        else:
            self.panel = pn.Column(self.text_pane, self.progress_indicator, **layout_params)

    @param.depends("text", watch=True)
    def _update_text(self):
        if self.text_pane:
            self.text_pane.object = self.text

    @param.depends("value", watch=True)
    def _update_value(self):
        if self.progress_indicator:
            self.progress_indicator.value = self.value

    @param.depends("max", watch=True)
    def _update_max(self):
        if self.progress_indicator:
            self.progress_indicator.max = self.max

    def __panel__(self):
        return self.panel

    def reset(self):
        """Resets the parameters"""
        self.value = self.param.value.default
        self.text = self.param.text.default

    def _get_tqdm(self):
        indicator = self
        class ptqdm(_tqdm):
            def display(self, msg=None, pos=None, bar_style=None):
                # display is used in Notebook
                if indicator.write_to_console:
                    super().display(msg, pos)

                indicator.max = self.total
                indicator.value = self.n
                indicator.text = self._to_text(**self.format_dict)
                return True

            def _to_text(self, n, total, **kwargs):
                return self.format_meter(n, total, **{**kwargs, "ncols": 0})

            def close(self):
                super().close()
                indicator.reset()
                return _tqdm
        return ptqdm


if __name__.startswith("bokeh"):
    import time
    tqdm = TQDMProgress(width=800, layout="column")
    def run(*events):
        for index in tqdm.tqdm(range(0,10)):
            time.sleep(0.2)
    button = pn.widgets.Button(name="run", button_type="success")
    button.on_click(run)
    app = pn.Column(
        button,
        tqdm,
        pn.Param(tqdm),
    ).servable()