from bokeh.models import ImportedStyleSheet

from panel.io.resources import CDN_DIST
from panel.theme.bootstrap import Bootstrap, Inherit
from panel.viewable import Viewable
from panel.widgets import TextInput


class CustomBootstrap(Bootstrap):

    modifiers = {
        Viewable: {
            'stylesheets': [Inherit, 'test.css']
        }
    }

def test_subclassed_inheritance():
    widget = TextInput()

    params, _ = CustomBootstrap().params(widget)
    assert 'stylesheets' in params
    assert len(params['stylesheets']) == 5
    s1, s2, s3, s4, s5 = params['stylesheets']
    assert isinstance(s1, ImportedStyleSheet)
    assert s1.url == f'{CDN_DIST}bundled/bootstrap5/css/bootstrap.min.css'
    assert isinstance(s2, ImportedStyleSheet)
    assert s2.url == f'{CDN_DIST}bundled/theme/default.css'
    assert isinstance(s3, ImportedStyleSheet)
    assert s3.url == f'{CDN_DIST}bundled/theme/bootstrap_default.css'
    assert isinstance(s4, ImportedStyleSheet)
    assert s4.url == f'{CDN_DIST}bundled/theme/bootstrap.css'
    assert s5 == '.bk-input {\n  color: red;\n}\n'


def test_subclassed_inheritance_server(server_document):
    widget = TextInput()

    params, _ = CustomBootstrap().params(widget)
    assert 'stylesheets' in params
    assert len(params['stylesheets']) == 5
    s1, s2, s3, s4, s5 = params['stylesheets']
    assert isinstance(s1, ImportedStyleSheet)
    assert s1.url == f'{CDN_DIST}bundled/bootstrap5/css/bootstrap.min.css'
    assert isinstance(s2, ImportedStyleSheet)
    assert s2.url == f'{CDN_DIST}bundled/theme/default.css'
    assert isinstance(s3, ImportedStyleSheet)
    assert s3.url == f'{CDN_DIST}bundled/theme/bootstrap_default.css'
    assert isinstance(s4, ImportedStyleSheet)
    assert s4.url == f'{CDN_DIST}bundled/theme/bootstrap.css'
    assert isinstance(s5, ImportedStyleSheet)
    assert s5.url == 'components/test_subclass/CustomBootstrap/modifiers/test.css'
