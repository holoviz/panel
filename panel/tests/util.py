import sys

from distutils.version import LooseVersion

import numpy as np
import pytest

try:
    import holoviews as hv
    hv_version = LooseVersion(hv.__version__)
except Exception:
    hv, hv_version = None, None
hv_available = pytest.mark.skipif(hv is None or hv_version < '1.13.0a23', reason="requires holoviews")

try:
    import matplotlib as mpl
    mpl.use('Agg')
except Exception:
    mpl = None
mpl_available = pytest.mark.skipif(mpl is None, reason="requires matplotlib")

try:
    import pandas as pd
except Exception:
    pd = None
pd_available = pytest.mark.skipif(pd is None, reason="requires pandas")

try:
    import streamz
except Exception:
    streamz = None
streamz_available = pytest.mark.skipif(streamz is None, reason="requires streamz")

try:
    import jupyter_bokeh
except Exception:
    jupyter_bokeh = None
jb_available = pytest.mark.skipif(jupyter_bokeh is None, reason="requires jupyter_bokeh")

py3_only = pytest.mark.skipif(sys.version_info.major < 3, reason="requires Python 3")

from panel.pane.markup import Markdown


def mpl_figure():
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(np.random.rand(10, 2))
    plt.close(fig)
    return fig


def check_layoutable_properties(layoutable, model):
    layoutable.background = '#ffffff'
    assert model.background == '#ffffff'

    layoutable.css_classes = ['custom_class']
    if isinstance(layoutable, Markdown):
        assert model.css_classes == ['custom_class', 'markdown']
    else:
        assert model.css_classes == ['custom_class']

    layoutable.width = 500
    assert model.width == 500

    layoutable.height = 450
    assert model.height == 450

    layoutable.min_height = 300
    assert model.min_height == 300

    layoutable.min_width = 250
    assert model.min_width == 250

    layoutable.max_height = 600
    assert model.max_height == 600

    layoutable.max_width = 550
    assert model.max_width == 550

    layoutable.margin = 10
    assert model.margin == (10, 10, 10, 10)

    layoutable.sizing_mode = 'stretch_width'
    assert model.sizing_mode == 'stretch_width'

    layoutable.width_policy = 'max'
    assert model.width_policy == 'max'

    layoutable.height_policy = 'min'
    assert model.height_policy == 'min'
