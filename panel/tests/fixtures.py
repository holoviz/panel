import pytest

import numpy as np
from bokeh.document import Document
from pyviz_comms import Comm


@pytest.fixture
def document():
    return Document()


@pytest.fixture
def comm():
    return Comm()


@pytest.yield_fixture
def hv_bokeh():
    import holoviews as hv
    hv.renderer('bokeh')
    prev_backend = hv.Store.current_backend
    hv.Store.current_backend = 'bokeh'
    yield
    hv.Store.current_backend = prev_backend


@pytest.yield_fixture
def hv_mpl():
    import holoviews as hv
    hv.renderer('matplotlib')
    prev_backend = hv.Store.current_backend
    hv.Store.current_backend = 'matplotlib'
    yield
    hv.Store.current_backend = prev_backend


def mpl_figure():
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(np.random.rand(10, 2))
    plt.close(fig)
    return fig
