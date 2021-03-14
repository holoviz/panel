# I did not put it into the indicators.py file yet as it raises errors due to circular imports I
# believe
import panel as pn
import param
from tqdm.auto import tqdm as _tqdm


EMPTY_TEXT = " "  # Hack: If set to None or "" the height of the text_pane is too little

MARGIN = {
    "text_pane": {"column": (5, 10, 0, 10), "row": (0, 10, 0, 10)},
    "progress_indicator": {"column": (0, 10, 5, 10), "row": (12, 10, 0, 10)},
}

# I cannot have it inherit from pn.indicators.BaseIndicator as that raises an exception
class Tqdm(pn.viewable.Viewer):
    value = param.Integer(
        default=0,
        bounds=(0, None),
        doc="""
        The current value of the progress bar. If set to None the progress
        bar will be indeterminate and animate depending on the active
        parameter.""",
    )
    max = param.Integer(default=100, doc="The maximum value of the progress bar.")
    text = param.String(default=EMPTY_TEXT)
    write_to_console = param.Boolean(
        default=False,
    )

    progress_indicator = param.ClassSelector(
        class_=pn.indicators.Progress,
        doc="""
        The Progress indicator to display to. Default is a pn.indicators.Progress
    """,
        precedence=-1,
    )
    text_pane = param.ClassSelector(
        class_=pn.pane.Str,
        doc="""
        The pane to display the text to. Default is a pn.pane.Str
    """,
        precedence=-1,
    )
    panel = param.ClassSelector(
        class_=(pn.Column, pn.Row),
        doc="""
        The panel to laying out the text_pane and progress_indicator. Default is a Column.
    """,
        precedence=-1,
    )

    tqdm = param.Parameter(precedence=-1)

    def __init__(self, layout="column", **params):
        if not "text_pane" in params:
            params["text_pane"] = pn.pane.Str(
                self.text, min_width=280, sizing_mode="fixed", margin=MARGIN["text_pane"][layout],
            )
        if not "progress_widget" in params:
            params["progress_indicator"] = pn.widgets.Progress(
                active=False,
                sizing_mode="stretch_width",
                min_width=100,
                margin=MARGIN["progress_indicator"][layout],
            )
        if not "tqdm" in params:
            params["tqdm"] = self._get_tqdm()

        layout_params = {}
        for key in params.copy():
            if hasattr(pn.layout.base.ListPanel, key):
                layout_params[key] = params.pop(key)

        super().__init__(**params)

        if self.value==0:
            # Hack: to give progress the initial look
            self.progress_indicator.max = 100000
            self.progress_indicator.value = 1
        else:
            self.progress_indicator.max = self.max
            self.progress_indicator.value = self.value
        self.text_pane = self.text_pane

        if layout == "row":
            self.panel = pn.Row(self.progress_indicator, self.text_pane, **layout_params)
        else:
            self.panel = pn.Column(self.text_pane, self.progress_indicator, **layout_params)

    def __call__(self, *args, **kwargs):
        return self.tqdm(*args, **kwargs)

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

                indicator.max = int(self.total) # Can be numpy.int64
                indicator.value = int(self.n)
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
    import pandas as pd
    import numpy as np

    tqdm = Tqdm(layout="row", sizing_mode="stretch_width")

    def run(*events):
        for index in tqdm(range(0, 10)):
            time.sleep(0.2)

    button = pn.widgets.Button(name="Run Loop", button_type="primary")
    button.on_click(run)

    # Register Pandas. This gives DataFrame.progress_apply method
    tqdm.tqdm.pandas(desc="my bar!")

    df = pd.DataFrame(np.random.randint(0, 100, (100000, 6)))

    def run_df(*events):
        df.progress_apply(lambda x: x**2)

    pandas_button = pn.widgets.Button(name="Pandas Apply", button_type="success")
    pandas_button.on_click(run_df)
    pandas_button

    component = pn.Column(
        button,
        pandas_button,
        tqdm,
        sizing_mode="stretch_width"
    )
    template = pn.template.FastListTemplate(
        title="Panel - Tqdm Indicator",
        main=[component],
        sidebar=[
            pn.Param(tqdm, sizing_mode="stretch_width"),
        ],
    )
    template.servable()
