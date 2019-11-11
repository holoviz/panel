from __future__ import absolute_import, division, unicode_literals

from panel import config
from panel.pane import Str

from .util import jb_available


@jb_available
def test_viewable_ipywidget():
    pane = Str('A')
    with config.set(comms='ipywidgets'):
        data, metadata = pane._repr_mimebundle_()
    assert 'application/vnd.jupyter.widget-view+json' in data
