import pathlib

from bokeh.models import ImportedStyleSheet

from panel.io.resources import CDN_DIST
from panel.theme.base import BOKEH_DARK, Design, Inherit
from panel.viewable import Viewable
from panel.widgets import FloatSlider, IntSlider, TextInput


def _custom_repr(self):
    try:
        return f"ImportedStyleSheet(url={self.url!r})"
    except Exception:
        return "ImportedStyleSheet(...)"

ImportedStyleSheet.__repr__ = _custom_repr  # type: ignore


class DesignTest(Design):

    modifiers = {
        IntSlider: {
            'stylesheets': [Inherit, 'http://example.com/baz.css']
        },
        FloatSlider: {
            'styles': {'color': 'red'},
            'stylesheets': [Inherit, pathlib.Path(__file__).parent / 'test.css']
        },
        TextInput: {
            'styles': {'color': 'green'},
            'stylesheets': [Inherit, '../theme/test.css']
        },
        Viewable: {
            'stylesheets': ['foo.css']
        }
    }


def test_design_params():
    widget = TextInput()

    params, _ = DesignTest().params(widget)
    assert 'stylesheets' in params
    assert len(params['stylesheets']) == 3
    s1, s2, s3 = params['stylesheets']
    assert isinstance(s1, ImportedStyleSheet)
    assert s1.url == f'{CDN_DIST}bundled/theme/default.css'
    assert isinstance(s2, ImportedStyleSheet)
    assert s2.url == 'foo.css'
    assert s3 == '.bk-input {\n  color: red;\n}\n'

    assert params.get('styles') == {'color': 'green'}

def test_design_params_server(server_document):
    widget = TextInput()

    params, _ = DesignTest().params(widget)
    assert 'stylesheets' in params
    assert len(params['stylesheets']) == 3
    s1, s2, s3 = params['stylesheets']
    assert isinstance(s1, ImportedStyleSheet)
    assert s1.url == f'{CDN_DIST}bundled/theme/default.css'
    assert isinstance(s2, ImportedStyleSheet)
    assert s2.url == 'foo.css'
    assert isinstance(s3, ImportedStyleSheet)
    assert s3.url == 'components/test_base/DesignTest/modifiers/test.css'

    assert params.get('styles') == {'color': 'green'}

def test_design_params_inherited():
    widget = FloatSlider()

    params, _ = DesignTest().params(widget)
    assert 'stylesheets' in params
    assert len(params['stylesheets']) == 3
    s1, s2, s3 = params['stylesheets']
    assert isinstance(s1, ImportedStyleSheet)
    assert s1.url == f'{CDN_DIST}bundled/theme/default.css'
    assert isinstance(s2, ImportedStyleSheet)
    assert s2.url == 'foo.css'
    assert s3 == '.bk-input {\n  color: red;\n}\n'

    assert params.get('styles') == {'color': 'red'}

def test_design_params_inherited_server(server_document):
    widget = FloatSlider()

    params, _ = DesignTest().params(widget)
    assert 'stylesheets' in params
    assert len(params['stylesheets']) == 3
    s1, s2, s3 = params['stylesheets']
    assert isinstance(s1, ImportedStyleSheet)
    assert s1.url == f'{CDN_DIST}bundled/theme/default.css'
    assert isinstance(s2, ImportedStyleSheet)
    assert s2.url == 'foo.css'
    assert isinstance(s3, ImportedStyleSheet)
    assert s3.url == 'components/test_base/DesignTest/modifiers/test.css'

    assert params.get('styles') == {'color': 'red'}

def test_design_params_url_inherited():
    widget = IntSlider()

    params, _ = DesignTest().params(widget)
    assert 'stylesheets' in params
    assert len(params['stylesheets']) == 3
    s1, s2, s3 = params['stylesheets']
    assert isinstance(s1, ImportedStyleSheet)
    assert s1.url == f'{CDN_DIST}bundled/theme/default.css'
    assert isinstance(s2, ImportedStyleSheet)
    assert s2.url == 'foo.css'
    assert isinstance(s3, ImportedStyleSheet)
    assert s3.url == 'http://example.com/baz.css'

def test_design_apply(document, comm):
    widget = TextInput()
    model = widget.get_root(document, comm=comm)

    DesignTest().apply(widget, model)

    assert len(model.stylesheets) == 5
    s1, s2, s3, s4, s5 = model.stylesheets
    assert isinstance(s1, str)
    assert 'pn-loading' in s1
    assert isinstance(s2, ImportedStyleSheet)
    assert s2.url.endswith('/dist/css/loading.css')
    assert isinstance(s3, ImportedStyleSheet)
    assert s3.url.endswith('/dist/bundled/theme/default.css')
    assert isinstance(s4, ImportedStyleSheet)
    assert s4.url.endswith('foo.css')
    assert s5 == '.bk-input {\n  color: red;\n}\n'
    assert model.styles == {'color': 'green'}

def test_design_apply_not_isolated(document, comm):
    widget = TextInput()
    model = widget.get_root(document, comm=comm)

    DesignTest().apply(widget, model, isolated=False)

    assert len(model.stylesheets) == 4
    s1, s2, s3, s4 = model.stylesheets
    assert isinstance(s1, str)
    assert 'pn-loading' in s1
    assert isinstance(s2, ImportedStyleSheet)
    assert s2.url.endswith('/dist/css/loading.css')
    assert isinstance(s3, ImportedStyleSheet)
    assert s3.url.endswith('foo.css')
    assert s4 == '.bk-input {\n  color: red;\n}\n'

    assert model.styles == {'color': 'green'}

def test_design_apply_inherited(document, comm):
    widget = FloatSlider()
    model = widget.get_root(document, comm=comm)

    DesignTest().apply(widget, model)

    assert len(model.stylesheets) == 5
    s1, s2, s3, s4, s5 = model.stylesheets
    assert isinstance(s1, str)
    assert 'pn-loading' in s1
    assert isinstance(s2, ImportedStyleSheet)
    assert s2.url.endswith('/dist/css/loading.css')
    assert isinstance(s3, ImportedStyleSheet)
    assert s3.url.endswith('/dist/bundled/theme/default.css')
    assert isinstance(s4, ImportedStyleSheet)
    assert s4.url.endswith('foo.css')
    assert s5 == '.bk-input {\n  color: red;\n}\n'

    assert model.styles == {'color': 'red'}

def test_design_apply_url_inherited(document, comm):
    widget = IntSlider()
    model = widget.get_root(document, comm=comm)

    DesignTest().apply(widget, model)

    assert len(model.stylesheets) == 5
    s1, s2, s3, s4, s5 = model.stylesheets
    assert isinstance(s1, str)
    assert 'pn-loading' in s1
    assert isinstance(s2, ImportedStyleSheet)
    assert s2.url.endswith('/dist/css/loading.css')
    assert isinstance(s3, ImportedStyleSheet)
    assert s3.url.endswith('/dist/bundled/theme/default.css')
    assert isinstance(s4, ImportedStyleSheet)
    assert s4.url.endswith('foo.css')
    assert isinstance(s5, ImportedStyleSheet)
    assert s5.url == 'http://example.com/baz.css'

def test_design_apply_with_dark_theme(document, comm):
    widget = TextInput()
    model = widget.get_root(document, comm=comm)
    model.document = document

    DesignTest(theme='dark').apply(widget, model)

    assert len(model.stylesheets) == 5
    s1, s2, s3, s4, s5 = model.stylesheets
    assert isinstance(s1, str)
    assert 'pn-loading' in s1
    assert isinstance(s2, ImportedStyleSheet)
    assert s2.url.endswith('/dist/css/loading.css')
    assert isinstance(s3, ImportedStyleSheet)
    assert s3.url.endswith('/dist/bundled/theme/dark.css')
    assert isinstance(s4, ImportedStyleSheet)
    assert s4.url.endswith('foo.css')
    assert s5 == '.bk-input {\n  color: red;\n}\n'

    assert document.theme._json == BOKEH_DARK

def test_design_apply_with_dark_theme_not_isolated(document, comm):
    widget = TextInput()
    model = widget.get_root(document, comm=comm)
    model.document = document

    DesignTest(theme='dark').apply(widget, model, isolated=False)

    assert len(model.stylesheets) == 4
    s1, s2, s3, s4 = model.stylesheets
    assert isinstance(s1, str)
    assert 'pn-loading' in s1
    assert isinstance(s2, ImportedStyleSheet)
    assert s2.url.endswith('/dist/css/loading.css')
    assert isinstance(s3, ImportedStyleSheet)
    assert s3.url.endswith('foo.css')
    assert s4 == '.bk-input {\n  color: red;\n}\n'

    assert document.theme._json == BOKEH_DARK

def test_design_apply_with_dist_url(document, comm):
    widget = TextInput()
    model = widget.get_root(document, comm=comm)
    model.document = document
    document._template_variables['dist_url'] = 'https://mock.holoviz.org/'

    DesignTest().apply(widget, model)

    assert len(model.stylesheets) == 5
    s1, s2, s3, s4, s5 = model.stylesheets
    assert isinstance(s1, str)
    assert 'pn-loading' in s1
    assert isinstance(s2, ImportedStyleSheet)
    assert s2.url.startswith('https://mock.holoviz.org/css/loading.css?v')
    assert isinstance(s3, ImportedStyleSheet)
    assert s3.url.startswith('https://mock.holoviz.org/bundled/theme/default.css?v')
    assert isinstance(s4, ImportedStyleSheet)
    assert s4.url == 'foo.css'
    assert s5 == '.bk-input {\n  color: red;\n}\n'

    assert model.styles == {'color': 'green'}

def test_design_apply_shared_stylesheet_models(document, comm):
    widget1 = TextInput()
    model1 = widget1.get_root(document, comm=comm)
    model1.document = document
    widget2 = TextInput()
    model2 = widget2.get_root(document, comm=comm)
    model2.document = document

    DesignTest().apply(widget1, model1)
    DesignTest().apply(widget2, model2)

    assert widget1.stylesheets == widget2.stylesheets
