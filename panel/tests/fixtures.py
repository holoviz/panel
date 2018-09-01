import pytest

from bokeh.document import Document
from pyviz_comms import Comm

@pytest.fixture
def document():
    return Document()

@pytest.fixture
def comm():
    return Comm()
