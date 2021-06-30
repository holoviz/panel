from functools import partial

import bokeh.core.properties as bp
import param

from bokeh.models import Div
from panel.layout import Tabs, WidgetBox
from panel.reactive import Reactive, ReactiveHTML
from panel.viewable import Viewable
from panel.widgets import Checkbox, StaticText, TextInput, IntInput


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


def test_link_properties_nb(document, comm):

    class ReactiveLink(Reactive):

        text = param.String(default='A')

    obj = ReactiveLink()
    div = Div()

    # Link property and check bokeh js property callback is defined
    obj._link_props(div, ['text'], document, div, comm)
    assert 'text' in div._callbacks

    # Assert callback is set up correctly
    cb = div._callbacks['text'][0]
    assert isinstance(cb, partial)
    assert cb.args == (document, div.ref['id'], comm)
    assert cb.func == obj._comm_change


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
    assert cb.args == (document, div.ref['id'])
    assert cb.func == obj._server_change


def test_text_input_controls():
    text_input = TextInput()

    controls = text_input.controls()

    assert isinstance(controls, Tabs)
    assert len(controls) == 2
    wb1, wb2 = controls
    assert isinstance(wb1, WidgetBox)
    assert len(wb1) == 6
    name, disabled, *(ws) = wb1

    assert isinstance(name, StaticText)
    assert isinstance(disabled, Checkbox)

    not_checked = []
    for w in ws:
        print(w.name)
        if w.name == 'Value':
            assert isinstance(w, TextInput)
            text_input.value = "New value"
            assert w.value == "New value"
        elif w.name == 'Value input':
            assert isinstance(w, TextInput)
        elif w.name == 'Placeholder':
            assert isinstance(w, TextInput)
            text_input.placeholder = "Test placeholder..."
            assert w.value == "Test placeholder..."
        elif w.name == 'Max length':
            assert isinstance(w, IntInput)
        else:
            not_checked.append(w)

    assert not not_checked

    assert isinstance(wb2, WidgetBox)
    assert len(wb2) == len(list(Viewable.param)) + 1



def test_text_input_controls_explicit():
    text_input = TextInput()

    controls = text_input.controls(['placeholder', 'disabled'])

    assert isinstance(controls, WidgetBox)
    assert len(controls) == 3
    name, disabled, placeholder = controls

    assert isinstance(name, StaticText)
    assert isinstance(disabled, Checkbox)
    assert isinstance(placeholder, TextInput)

    text_input.disabled = True
    assert disabled.value

    text_input.placeholder = "Test placeholder..."
    assert placeholder.value == "Test placeholder..."


def test_reactive_html_basic():

    class Test(ReactiveHTML):

        int = param.Integer(default=3, doc='An integer')

        float = param.Number(default=3.14, doc='A float')

        _template = '<div id="div" width=${int}></div>'

    data_model = Test._data_model
    assert data_model.__name__ == 'Test1'

    properties = data_model.properties()
    assert 'int' in properties
    assert 'float' in properties

    int_prop = data_model.lookup('int')
    assert isinstance(int_prop.property, bp.Int)
    assert int_prop.class_default(data_model) == 3

    float_prop = data_model.lookup('float')
    assert isinstance(float_prop.property, bp.Float)
    assert float_prop.class_default(data_model) == 3.14

    assert Test._attrs == {'div': [('width', ['int'], '{int}')]}
    assert Test._node_callbacks == {}


    test = Test()
    root = test.get_root()
    assert root.callbacks == {}
    assert root.events == {}


def test_reactive_html_dom_events():

    class TestDOMEvents(ReactiveHTML):

        int = param.Integer(default=3, doc='An integer')

        float = param.Number(default=3.14, doc='A float')

        _template = '<div id="div" width=${int}></div>'

        _dom_events = {'div': ['change']}

    data_model = TestDOMEvents._data_model
    assert data_model.__name__ == 'TestDOMEvents1'

    properties = data_model.properties()
    assert 'int' in properties
    assert 'float' in properties

    int_prop = data_model.lookup('int')
    assert isinstance(int_prop.property, bp.Int)
    assert int_prop.class_default(data_model) == 3

    float_prop = data_model.lookup('float')
    assert isinstance(float_prop.property, bp.Float)
    assert float_prop.class_default(data_model) == 3.14

    assert TestDOMEvents._attrs == {'div': [('width', ['int'], '{int}')]}
    assert TestDOMEvents._node_callbacks == {}

    test = TestDOMEvents()
    root = test.get_root()
    assert root.callbacks == {}
    assert root.events == {'div': {'change': True}}


def test_reactive_html_inline():
    class TestInline(ReactiveHTML):

        int = param.Integer(default=3, doc='An integer')

        _template = '<div id="div" onchange=${_div_change} width=${int}></div>'

        def _div_change(self, event):
            pass

    data_model = TestInline._data_model
    assert data_model.__name__ == 'TestInline1'

    properties = data_model.properties()
    assert 'int' in properties

    int_prop = data_model.lookup('int')
    assert isinstance(int_prop.property, bp.Int)
    assert int_prop.class_default(data_model) == 3

    assert TestInline._attrs == {
        'div': [
            ('onchange', [], '{_div_change}'),
            ('width', ['int'], '{int}')
        ]
    }
    assert TestInline._node_callbacks == {'div': [('onchange', '_div_change')]}
    assert TestInline._inline_callbacks == [('div', 'onchange', '_div_change')]

    test = TestInline()
    root = test.get_root()
    assert root.callbacks == {'div': [('onchange', '_div_change')]}
    assert root.events == {}

    test.on_event('div', 'click', print)
    assert root.events == {'div': {'click': False}}


def test_reactive_html_children():

    class TestChildren(ReactiveHTML):

        children = param.List(default=[])

        _template = '<div id="div">${children}</div>'

    assert TestChildren._attrs == {}
    assert TestChildren._node_callbacks == {}
    assert TestChildren._inline_callbacks == []
    assert TestChildren._parser.children == {'div': 'children'}

    widget = TextInput()
    test = TestChildren(children=[widget])
    root = test.get_root()
    assert root.children == {'div': [widget._models[root.ref['id']][0]]}

    widget_new = TextInput()
    test.children = [widget_new]
    assert len(widget._models) == 0
    assert root.children == {'div': [widget_new._models[root.ref['id']][0]]}



def test_reactive_html_templated_children():

    class TestTemplatedChildren(ReactiveHTML):

        children = param.List(default=[])

        _template = """
        <select id="select">
        {% for option in children %}
        <option id="option-{{ loop.index0 }}">${children[{{ loop.index0 }}]}</option>
        {% endfor %}
        </div>
        """

    assert TestTemplatedChildren._attrs == {}
    assert TestTemplatedChildren._node_callbacks == {}
    assert TestTemplatedChildren._inline_callbacks == []
    assert TestTemplatedChildren._parser.children == {'option': 'children'}

    widget = TextInput()
    test = TestTemplatedChildren(children=[widget])
    root = test.get_root()
    assert root.looped == ['option']
    assert root.children == {'option': [widget._models[root.ref['id']][0]]}

    widget_new = TextInput()
    test.children = [widget_new]
    assert len(widget._models) == 0
    assert root.children == {'option': [widget_new._models[root.ref['id']][0]]}



def test_reactive_html_templated_children_add_loop_id():

    class TestTemplatedChildren(ReactiveHTML):

        children = param.List(default=[])

        _template = """
        <select id="select">
        {% for option in children %}
          <option id="option">${children[{{ loop.index0 }}]}</option>
        {% endfor %}
        </select>
        """

    assert TestTemplatedChildren._attrs == {}
    assert TestTemplatedChildren._node_callbacks == {}
    assert TestTemplatedChildren._inline_callbacks == []
    assert TestTemplatedChildren._parser.children == {'option': 'children'}

    test = TestTemplatedChildren(children=['A', 'B', 'C'])

    assert test._get_template() == """
        <select id="select-${id}">
        
          <option id="option-0-${id}"></option>
        
          <option id="option-1-${id}"></option>
        
          <option id="option-2-${id}"></option>
        
        </select>
        """

    model = test.get_root()
    assert model.looped == ['option']



def test_reactive_html_templated_children_add_loop_id_and_for_loop_var():

    class TestTemplatedChildren(ReactiveHTML):

        children = param.List(default=[])

        _template = """
        <select id="select">
        {% for option in children %}
          <option id="option">${option}</option>
        {% endfor %}
        </select>
        """

    assert TestTemplatedChildren._attrs == {}
    assert TestTemplatedChildren._node_callbacks == {}
    assert TestTemplatedChildren._inline_callbacks == []
    assert TestTemplatedChildren._parser.children == {'option': 'children'}

    test = TestTemplatedChildren(children=['A', 'B', 'C'])

    assert test._get_template() == """
        <select id="select-${id}">
        
          <option id="option-0-${id}"></option>
        
          <option id="option-1-${id}"></option>
        
          <option id="option-2-${id}"></option>
        
        </select>
        """
    model = test.get_root()
    assert model.looped == ['option']
