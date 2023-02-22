from bokeh.models import ImportedStyleSheet

from panel.theme.base import BOKEH_DARK, Design, Inherit
from panel.viewable import Viewable
from panel.widgets import FloatSlider, IntSlider, TextInput


class DesignTest(Design):

    _modifiers = {
        IntSlider: {
            'stylesheets': [Inherit, 'http://example.com/baz.css']
        },
        FloatSlider: {
            'styles': {'color': 'red'},
            'stylesheets': [Inherit, 'bar.css']
        },
        TextInput: {
            'styles': {'color': 'green'}
        },
        Viewable: {
            'stylesheets': ['foo.css']
        }
    }


def test_design_params():
    widget = TextInput()

    params, _ = DesignTest().params(widget)
    assert 'stylesheets' in params
    assert len(params['stylesheets']) == 2
    s1, s2 = params['stylesheets']
    assert isinstance(s1, ImportedStyleSheet)
    assert s1.url == 'bundled/defaulttheme/default.css'
    assert isinstance(s2, ImportedStyleSheet)
    assert s2.url == 'bundled/designtest/foo.css'

    assert params.get('styles') == {'color': 'green'}

def test_design_params_inherited():
    widget = FloatSlider()

    params, _ = DesignTest().params(widget)
    assert 'stylesheets' in params
    assert len(params['stylesheets']) == 3
    s1, s2, s3 = params['stylesheets']
    assert isinstance(s1, ImportedStyleSheet)
    assert s1.url == 'bundled/defaulttheme/default.css'
    assert isinstance(s2, ImportedStyleSheet)
    assert s2.url == 'bundled/designtest/foo.css'
    assert isinstance(s3, ImportedStyleSheet)
    assert s3.url == 'bundled/designtest/bar.css'

    assert params.get('styles') == {'color': 'red'}

def test_design_params_url_inherited():
    widget = IntSlider()

    params, _ = DesignTest().params(widget)
    assert 'stylesheets' in params
    assert len(params['stylesheets']) == 3
    s1, s2, s3 = params['stylesheets']
    assert isinstance(s1, ImportedStyleSheet)
    assert s1.url == 'bundled/defaulttheme/default.css'
    assert isinstance(s2, ImportedStyleSheet)
    assert s2.url == 'bundled/designtest/foo.css'
    assert isinstance(s3, ImportedStyleSheet)
    assert s3.url == 'http://example.com/baz.css'

def test_design_apply(document, comm):
    widget = TextInput()
    model = widget.get_root(document, comm=comm)

    DesignTest().apply(widget, model)

    assert len(model.stylesheets) == 3
    s1, s2, s3 = model.stylesheets
    assert isinstance(s1, str)
    assert 'pn-loading' in s1
    assert isinstance(s2, ImportedStyleSheet)
    assert s2.url.endswith('/dist/bundled/defaulttheme/default.css')
    assert isinstance(s3, ImportedStyleSheet)
    assert s3.url.endswith('/dist/bundled/designtest/foo.css')

    assert model.styles == {'color': 'green'}

def test_design_apply_not_isolated(document, comm):
    widget = TextInput()
    model = widget.get_root(document, comm=comm)

    DesignTest().apply(widget, model, isolated=False)

    assert len(model.stylesheets) == 2
    s1, s2 = model.stylesheets
    assert isinstance(s1, str)
    assert 'pn-loading' in s1
    assert isinstance(s2, ImportedStyleSheet)
    assert s2.url.endswith('/dist/bundled/designtest/foo.css')

    assert model.styles == {'color': 'green'}

def test_design_apply_inherited(document, comm):
    widget = FloatSlider()
    model = widget.get_root(document, comm=comm)

    DesignTest().apply(widget, model)

    assert len(model.stylesheets) == 4
    s1, s2, s3, s4 = model.stylesheets
    assert isinstance(s1, str)
    assert 'pn-loading' in s1
    assert isinstance(s2, ImportedStyleSheet)
    assert s2.url.endswith('/dist/bundled/defaulttheme/default.css')
    assert isinstance(s3, ImportedStyleSheet)
    assert s3.url.endswith('/dist/bundled/designtest/foo.css')
    assert isinstance(s4, ImportedStyleSheet)
    assert s4.url.endswith('/dist/bundled/designtest/bar.css')

    assert model.styles == {'color': 'red'}

def test_design_apply_url_inherited(document, comm):
    widget = IntSlider()
    model = widget.get_root(document, comm=comm)

    DesignTest().apply(widget, model)

    assert len(model.stylesheets) == 4
    s1, s2, s3, s4 = model.stylesheets
    assert isinstance(s1, str)
    assert 'pn-loading' in s1
    assert isinstance(s2, ImportedStyleSheet)
    assert s2.url.endswith('/dist/bundled/defaulttheme/default.css')
    assert isinstance(s3, ImportedStyleSheet)
    assert s3.url.endswith('/dist/bundled/designtest/foo.css')
    assert isinstance(s4, ImportedStyleSheet)
    assert s4.url == 'http://example.com/baz.css'

def test_design_apply_with_dark_theme(document, comm):
    widget = TextInput()
    model = widget.get_root(document, comm=comm)
    model.document = document

    DesignTest(theme='dark').apply(widget, model)

    assert len(model.stylesheets) == 3
    s1, s2, s3 = model.stylesheets
    assert isinstance(s1, str)
    assert 'pn-loading' in s1
    assert isinstance(s2, ImportedStyleSheet)
    assert s2.url.endswith('/dist/bundled/darktheme/dark.css')
    assert isinstance(s3, ImportedStyleSheet)
    assert s3.url.endswith('/dist/bundled/designtest/foo.css')

    assert document.theme._json == BOKEH_DARK

def test_design_apply_with_dark_theme_not_isolated(document, comm):
    widget = TextInput()
    model = widget.get_root(document, comm=comm)
    model.document = document

    DesignTest(theme='dark').apply(widget, model, isolated=False)

    assert len(model.stylesheets) == 2
    s1, s2 = model.stylesheets
    assert isinstance(s1, str)
    assert 'pn-loading' in s1
    assert isinstance(s2, ImportedStyleSheet)
    assert s2.url.endswith('/dist/bundled/designtest/foo.css')

    assert document.theme._json == BOKEH_DARK

def test_design_apply_with_dist_url(document, comm):
    widget = TextInput()
    model = widget.get_root(document, comm=comm)
    model.document = document
    document._template_variables['dist_url'] = 'https://mock.holoviz.org/'

    DesignTest().apply(widget, model)

    assert len(model.stylesheets) == 3
    s1, s2, s3 = model.stylesheets
    assert isinstance(s1, str)
    assert 'pn-loading' in s1
    assert isinstance(s2, ImportedStyleSheet)
    assert s2.url == 'https://mock.holoviz.org/bundled/defaulttheme/default.css'
    assert isinstance(s3, ImportedStyleSheet)
    assert s3.url == 'https://mock.holoviz.org/bundled/designtest/foo.css'

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
