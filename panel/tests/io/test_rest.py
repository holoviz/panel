import param
import pytest

from panel.io.state import state
from panel.util.warnings import PanelDeprecationWarning


class Published(param.Parameterized):

    value = param.Integer(default=1)


def test_state_publish_is_deprecated():
    try:
        with pytest.warns(PanelDeprecationWarning, match="'pn.state.publish' is deprecated"):
            state.publish('deprecated', Published())
    finally:
        state._rest_endpoints.pop('deprecated', None)
