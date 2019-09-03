"""
A module containing testing utilities and fixtures.
"""
from __future__ import absolute_import, division, unicode_literals

import re
import shutil
    
import pytest

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


@pytest.yield_fixture
def tmpdir(request, tmpdir_factory):
    name = request.node.name
    name = re.sub("[\W]", "_", name)
    MAXVAL = 30
    if len(name) > MAXVAL:
        name = name[:MAXVAL]
    tmp_dir = tmpdir_factory.mktemp(name, numbered=True)
    yield tmp_dir
    shutil.rmtree(str(tmp_dir))
