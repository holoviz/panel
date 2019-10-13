from __future__ import absolute_import, division, unicode_literals

import numpy as np
import pytest

try:
    import holoviews as hv
except:
    hv = None
hv_available = pytest.mark.skipif(hv is None, reason="requires holoviews")

try:
    import matplotlib as mpl
    mpl.use('Agg')
except:
    mpl = None
mpl_available = pytest.mark.skipif(mpl is None, reason="requires matplotlib")


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
