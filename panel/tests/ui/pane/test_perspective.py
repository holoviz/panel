import pandas as pd
import pytest

from panel.pane import Perspective
from panel.tests.util import serve_component

pytestmark = pytest.mark.ui

def test_perspective_no_console_errors(page, port):
    perspective = Perspective(pd._testing.makeMixedDataFrame())

    msgs = serve_component(page, port, perspective)

    page.wait_for_timeout(1000)

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []
