from functools import partial

import param

from bokeh.models import Div, Row as BkRow
from panel.viewable import Reactive


def test_link():
    "Link two Reactive objects"

    class ReactiveLink(Reactive):

        a = param.Parameter()

    obj = ReactiveLink()
    obj2 = ReactiveLink()
    obj.link(obj2, a='a')
    obj.a = 1

    assert obj.a == 1
    assert obj2.a == 1

    obj._cleanup(None, final=True)
    assert obj._callbacks == {}


def test_param_rename():
    "Test that Reactive renames params and properties"

    class ReactiveRename(Reactive):

        a = param.Parameter()
    
        _rename = {'a': 'b'}

    obj = ReactiveRename()

    params = obj._process_property_change({'b': 1})
    assert params == {'a': 1}

    properties = obj._process_param_change({'a': 1})
    assert properties == {'b': 1}


def test_link_params_nb(document, comm):

    class ReactiveLink(Reactive):

        text = param.String(default='A')

    root = BkRow()
    obj = ReactiveLink()
    div = Div()

    # Link params and ensure callback is cached
    obj._link_params(div, ['text'], document, root, comm)
    assert root.ref['id'] in obj._callbacks

    # Set object parameter and assert bokeh property updates
    obj.text = 'B'
    assert div.text == 'B'

    # Assert cleanup deletes callback
    obj._cleanup(root, True)
    assert obj._callbacks == {}


def test_link_properties_nb(document, comm):

    class ReactiveLink(Reactive):

        text = param.String(default='A')

    obj = ReactiveLink()
    div = Div()

    # Link property and check bokeh js property callback is defined
    obj._link_props(div, ['text'], document, div, comm)
    assert 'change:text' in div.js_property_callbacks

    # Assert CustomJS callback contains root id
    customjs = div.js_property_callbacks['change:text'][0]
    assert div.ref['id'] in customjs.code


def test_link_properties_server(document):

    class ReactiveLink(Reactive):

        text = param.String(default='A')

    obj = ReactiveLink()
    div = Div()

    # Link property and check bokeh callback is defined
    obj._link_props(div, ['text'], document, div)
    assert 'text' in div._callbacks

    # Assert callback is set up correctly
    cb = div._callbacks['text'][0]
    assert isinstance(cb, partial)
    assert cb.args == (document,)
    assert cb.func == obj._server_change
