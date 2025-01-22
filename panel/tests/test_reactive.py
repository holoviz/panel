from __future__ import annotations

import asyncio
import unittest.mock

from functools import partial

import bokeh.core.properties as bp
import param
import pytest

from bokeh.document import Document
from bokeh.io.doc import patch_curdoc
from bokeh.models import Div

from panel.depends import bind, depends
from panel.io.state import set_curdoc
from panel.layout import Tabs, WidgetBox
from panel.pane import Markdown
from panel.reactive import Reactive, ReactiveHTML
from panel.viewable import Viewable
from panel.widgets import (
    Checkbox, IntInput, IntSlider, StaticText, TextInput,
)


def test_reactive_default_title():
    doc = ReactiveHTML().server_doc()

    assert doc.title == 'Panel Application'


def test_reactive_servable_title():
    doc = Document()

    session_context = unittest.mock.Mock()

    with patch_curdoc(doc):
        doc._session_context = lambda: session_context
        ReactiveHTML().servable(title='A')
        ReactiveHTML().servable(title='B')

    assert doc.title == 'B'


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
    assert cb.args == (document, div.ref['id'], comm, None)
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
    assert cb.args == (document, div.ref['id'], None)
    assert cb.func == obj._server_change


def test_text_input_controls():
    text_input = TextInput()

    controls = text_input.controls()

    assert isinstance(controls, Tabs)
    assert len(controls) == 2
    wb1, wb2 = controls
    assert isinstance(wb1, WidgetBox)
    assert len(wb1) == 7
    name, value, disabled, *(ws) = wb1

    assert isinstance(value, TextInput)
    text_input.value = "New value"
    assert value.value == "New value"
    assert isinstance(name, StaticText)
    assert isinstance(disabled, Checkbox)

    not_checked = []
    for w in ws:
        if w.name == 'Value input':
            assert isinstance(w, TextInput)
        elif w.name == 'Placeholder':
            assert isinstance(w, TextInput)
            text_input.placeholder = "Test placeholder..."
            assert w.value == "Test placeholder..."
        elif w.name == 'Max length':
            assert isinstance(w, IntInput)
        elif w.name == 'Description':
            assert isinstance(w, TextInput)
            text_input.description = "Test description..."
            assert w.value == "Test description..."
        else:
            not_checked.append(w)

    assert not not_checked

    assert isinstance(wb2, WidgetBox)

    params1 = {w.name.replace(" ", "_").lower() for w in wb2 if len(w.name)}
    params2 = set(Viewable.param) - {"background", "design", "stylesheets", "loading"}
    # Background should be moved when Layoutable.background is removed.

    assert not len(params1 - params2)
    assert not len(params2 - params1)

def test_pass_widget_by_reference():
    int_input = IntInput(start=0, end=400, value=42)
    text_input = TextInput(width=int_input)

    assert text_input.width == 42

    int_input.value = 101

    assert text_input.width == 101

def test_pass_param_by_reference():
    int_input = IntInput(start=0, end=400, value=42)
    text_input = TextInput(width=int_input.param.value)

    assert text_input.width == 42

    int_input.value = 101

    assert text_input.width == 101

def test_pass_bind_function_by_reference():
    int_input = IntInput(start=0, end=400, value=42)
    fn = bind(lambda v: v + 10, int_input)
    text_input = TextInput(width=fn)

    assert text_input.width == 52

    int_input.value = 101

    assert text_input.width == 111

async def test_pass_bind_async_func_by_reference():
    int_input = IntInput(start=0, end=400, value=42)

    async def gen(v):
        return v + 10

    text_input = TextInput(width=bind(gen, int_input))

    await asyncio.sleep(0.01)
    assert text_input.width == 52

    int_input.value = 101

    await asyncio.sleep(0.01)
    assert text_input.width == 111

async def test_pass_bind_async_generator_by_reference():
    int_input = IntInput(start=0, end=400, value=42)

    async def gen(v):
        yield v + 10

    text_input = TextInput(width=bind(gen, int_input))

    await asyncio.sleep(0.01)
    assert text_input.width == 52

    int_input.value = 101

    await asyncio.sleep(0.01)
    assert text_input.width == 111

async def test_pass_bind_multi_async_generator_by_reference():
    int_input = IntInput(start=0, end=400, value=42)

    async def gen(v):
        yield v + 10
        yield v + 20

    text_input = TextInput(width=bind(gen, int_input))

    widths = []
    text_input.param.watch(lambda e: widths.append(e.new), 'width')

    await asyncio.sleep(0.01)
    assert text_input.width == 62

    int_input.value = 101

    await asyncio.sleep(0.01)
    assert widths == [52, 62, 111, 121]
    assert text_input.width == 121

def test_pass_refs():
    slider = IntSlider(value=5, start=1, end=10, name='Number')
    size = IntSlider(value=12, start=6, end=24, name='Size')

    def refs(number, size):
        return {
            'object': '*' * number,
            'styles': {'font-size': f'{size}pt'}
        }

    irefs = bind(refs, slider, size)

    md = Markdown(refs=irefs)

    assert md.object == '*****'
    assert md.styles == {'font-size': '12pt'}

    slider.value = 3
    assert md.object == '***'

    size.value = 7
    assert md.styles == {'font-size': '7pt'}

async def test_pass_refs_async():
    async def refs():
        yield {
            'object': '*****',
            'styles': {'font-size': '12pt'}
        }
        await asyncio.sleep(0.1)
        yield {
            'object': '***',
            'styles': {'font-size': '7pt'}
        }

    md = Markdown(refs=refs)

    await asyncio.sleep(0.01)

    assert md.object == '*****'
    assert md.styles == {'font-size': '12pt'}

    await asyncio.sleep(0.1)

    assert md.object == '***'
    assert md.styles == {'font-size': '7pt'}

async def test_pass_bind_multi_async_generator_by_reference_and_abort():
    int_input = IntInput(start=0, end=400, value=42)

    async def gen(v):
        yield v + 10
        await asyncio.sleep(0.1)
        yield v + 20

    text_input = TextInput(width=bind(gen, int_input))

    await asyncio.sleep(0.01)
    assert text_input.width == 52
    int_input.value = 101
    await asyncio.sleep(0.01)
    assert text_input.width == 111
    await asyncio.sleep(0.1)
    assert text_input.width == 121

def test_pass_parameterized_method_by_reference():

    class Test(param.Parameterized):

        a = param.Parameter(default=1)
        b = param.Parameter(default=2)

        @param.depends('a')
        def dep_a(self):
            return self.a

        @param.depends('dep_a', 'b')
        def dep_ab(self):
            return self.dep_a() + self.b

    test = Test()
    int_input = IntInput(start=0, end=400, value=test.dep_ab)

    assert int_input.value == 3

    test.a = 3

    assert int_input.value == 5

    test.b = 5

    assert int_input.value == 8

def test_pass_depends_function_by_reference():
    int_input = IntInput(start=0, end=400, value=42)
    fn = depends(int_input)(lambda v: v + 10)
    text_input = TextInput(width=fn)

    assert text_input.width == 52

    int_input.value = 101

    assert text_input.width == 111

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

def test_property_change_does_not_boomerang(document, comm):
    text_input = TextInput(value='A')

    model = text_input.get_root(document, comm)

    assert model.value == 'A'
    model.value = 'B'
    with set_curdoc(document):
        text_input._process_events({'value': 'C'})

    assert model.value == 'B'
    assert text_input.value == 'C'

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

    assert Test._node_callbacks == {}

    test = Test()
    root = test.get_root()
    assert test._attrs == {'div': [('width', ['int'], '{int}')]}
    assert root.callbacks == {}
    assert root.events == {}

def test_reactive_html_no_id_param_error():

    with pytest.raises(ValueError) as excinfo:
        class Test(ReactiveHTML):
            width = param.Number(default=200)

            _template = '<div width=${width}></div>'

    assert "Found <div> node with the `width` attribute referencing the `width` parameter." in str(excinfo.value)

def test_reactive_html_no_id_method_error():

    with pytest.raises(ValueError) as excinfo:
        class Test(ReactiveHTML):

            _template = '<div onclick=${_onclick}></div>'

            def _onclick(self):
                pass
    assert "Found <div> node with the `onclick` callback referencing the `_onclick` method." in str(excinfo.value)

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

    assert TestDOMEvents._node_callbacks == {}

    test = TestDOMEvents()
    root = test.get_root()
    assert test._attrs == {'div': [('width', ['int'], '{int}')]}
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

    assert TestInline._node_callbacks == {'div': [('onchange', '_div_change')]}
    assert TestInline._inline_callbacks == [('div', 'onchange', '_div_change')]

    test = TestInline()
    root = test.get_root()
    assert test._attrs == {
        'div': [
            ('onchange', [], '{_div_change}'),
            ('width', ['int'], '{int}')
        ]
    }
    assert root.callbacks == {'div': [('onchange', '_div_change')]}
    assert root.events == {}

    test.on_event('div', 'click', print)
    assert root.events == {'div': {'click': False}}

def test_reactive_html_children():

    class TestChildren(ReactiveHTML):

        children = param.List(default=[])

        _template = '<div id="div">${children}</div>'

    assert TestChildren._node_callbacks == {}
    assert TestChildren._inline_callbacks == []
    assert TestChildren._parser.children == {'div': 'children'}

    widget = TextInput()
    test = TestChildren(children=[widget])
    root = test.get_root()
    assert test._attrs == {}
    assert root.children == {'div': [widget._models[root.ref['id']][0]]}
    assert len(widget._models) == 1
    assert test._panes == {'children': [widget]}

    widget_new = TextInput()
    test.children = [widget_new]
    assert len(widget._models) == 0
    assert root.children == {'div': [widget_new._models[root.ref['id']][0]]}
    assert test._panes == {'children': [widget_new]}

    test._cleanup(root)
    assert len(test._models) == 0
    assert len(widget_new._models) == 0

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

    assert TestTemplatedChildren._node_callbacks == {}
    assert TestTemplatedChildren._inline_callbacks == []
    assert TestTemplatedChildren._parser.children == {'option': 'children'}

    widget = TextInput()
    test = TestTemplatedChildren(children=[widget])
    root = test.get_root()
    assert test._attrs == {}
    assert root.looped == ['option']
    assert root.children == {'option': [widget._models[root.ref['id']][0]]}
    assert test._panes == {'children': [widget]}

    widget_new = TextInput()
    test.children = [widget_new]
    assert len(widget._models) == 0
    assert root.children == {'option': [widget_new._models[root.ref['id']][0]]}
    assert test._panes == {'children': [widget_new]}

def test_reactive_html_templated_dict_children():

    class TestTemplatedChildren(ReactiveHTML):

        children = param.Dict(default={})

        _template = """
        <select id="select">
        {% for key, option in children.items() %}
        <option id="option-{{ loop.index0 }}">${children[{{ key }}]}</option>
        {% endfor %}
        </div>
        """

    assert TestTemplatedChildren._node_callbacks == {}
    assert TestTemplatedChildren._inline_callbacks == []
    assert TestTemplatedChildren._parser.children == {'option': 'children'}

    widget = TextInput()
    test = TestTemplatedChildren(children={'test': widget})
    root = test.get_root()
    assert test._attrs == {}
    assert root.looped == ['option']
    assert root.children == {'option': [widget._models[root.ref['id']][0]]}
    assert test._panes == {'children': [widget]}
    widget_model = widget._models[root.ref['id']][0]

    widget_new = TextInput()
    test.children = {'test': widget_new, 'test2': widget}
    assert len(widget._models) == 1
    assert root.children == {
        'option': [
            widget_new._models[root.ref['id']][0],
            widget_model
        ]
    }
    assert test._panes == {'children': [widget_new, widget]}

def test_reactive_html_templated_children_add_loop_id():

    class TestTemplatedChildren(ReactiveHTML):

        children = param.List(default=[])

        _template = """
        <select id="select">
        {%- for option in children %}
          <option id="option">${children[{{ loop.index0 }}]}</option>
        {%- endfor %}
        </select>
        """

    assert TestTemplatedChildren._node_callbacks == {}
    assert TestTemplatedChildren._inline_callbacks == []
    assert TestTemplatedChildren._parser.children == {'option': 'children'}

    test = TestTemplatedChildren(children=['A', 'B', 'C'])

    assert test._get_template()[0] == """
        <select id="select-${id}">
          <option id="option-0-${id}"></option>
          <option id="option-1-${id}"></option>
          <option id="option-2-${id}"></option>
        </select>
        """

    model = test.get_root()
    assert test._attrs == {}
    assert model.looped == ['option']

def test_reactive_html_templated_children_add_loop_id_and_for_loop_var():

    class TestTemplatedChildren(ReactiveHTML):

        children = param.List(default=[])

        _template = """
        <select id="select">
        {%- for option in children %}
          <option id="option">${option}</option>
        {%- endfor %}
        </select>
        """

    assert TestTemplatedChildren._node_callbacks == {}
    assert TestTemplatedChildren._inline_callbacks == []
    assert TestTemplatedChildren._parser.children == {'option': 'children'}

    test = TestTemplatedChildren(children=['A', 'B', 'C'])

    assert test._get_template()[0] == """
        <select id="select-${id}">
          <option id="option-0-${id}"></option>
          <option id="option-1-${id}"></option>
          <option id="option-2-${id}"></option>
        </select>
        """
    model = test.get_root()
    assert test._attrs == {}
    assert model.looped == ['option']

def test_reactive_html_templated_children_add_loop_id_and_for_loop_var_insensitive_to_spaces():

    class TestTemplatedChildren(ReactiveHTML):

        children = param.List(default=[])

        _template = """
        <select id="select">
        {%- for option in children %}
          <option id="option">${ option   }</option>
        {%- endfor %}
        </select>
        """

    assert TestTemplatedChildren._node_callbacks == {}
    assert TestTemplatedChildren._inline_callbacks == []
    assert TestTemplatedChildren._parser.children == {'option': 'children'}

    test = TestTemplatedChildren(children=['A', 'B', 'C'])

    assert test._get_template()[0] == """
        <select id="select-${id}">
          <option id="option-0-${id}"></option>
          <option id="option-1-${id}"></option>
          <option id="option-2-${id}"></option>
        </select>
        """
    model = test.get_root()
    assert test._attrs == {}
    assert model.looped == ['option']

def test_reactive_html_scripts_linked_properties_assignment_operator():

    for operator in ['', '+', '-', '*', '\\', '%', '**', '>>', '<<', '>>>', '&', '^', '&&', '||', '??']:
        for sep in [' ', '']:

            class TestScripts(ReactiveHTML):

                clicks = param.Integer()

                _template = "<div id='test'></div>"

                _scripts = {'render': f'test.onclick = () => {{ data.clicks{sep}{operator}= 1 }}'}

            assert TestScripts()._linked_properties == ('clicks',)

def test_reactive_html_templated_literal_add_loop_id_and_for_loop_var():

    class TestTemplatedChildren(ReactiveHTML):

        children = param.List(default=[])

        _template = """
        <select id="select">
        {%- for option in children %}
          <option id="option">{{ option }}</option>
        {%- endfor %}
        </select>
        """

    assert TestTemplatedChildren._node_callbacks == {}
    assert TestTemplatedChildren._inline_callbacks == []
    assert TestTemplatedChildren._parser.children == {}

    test = TestTemplatedChildren(children=['A', 'B', 'C'])

    assert test._get_template()[0] == """
        <select id="select-${id}">
          <option id="option-0-${id}">A</option>
          <option id="option-1-${id}">B</option>
          <option id="option-2-${id}">C</option>
        </select>
        """
    model = test.get_root()
    assert test._attrs == {}
    assert model.looped == ['option']

def test_reactive_html_templated_literal_add_loop_id_and_for_loop_var_insensitive_to_spaces():

    class TestTemplatedChildren(ReactiveHTML):

        children = param.List(default=[])

        _template = """
        <select id="select">
        {%- for option in children %}
          <option id="option">{{option   }}</option>
        {%- endfor %}
        </select>
        """

    assert TestTemplatedChildren._node_callbacks == {}
    assert TestTemplatedChildren._inline_callbacks == []
    assert TestTemplatedChildren._parser.children == {}

    test = TestTemplatedChildren(children=['A', 'B', 'C'])

    assert test._get_template()[0] == """
        <select id="select-${id}">
          <option id="option-0-${id}">A</option>
          <option id="option-1-${id}">B</option>
          <option id="option-2-${id}">C</option>
        </select>
        """
    model = test.get_root()
    assert test._attrs == {}
    assert model.looped == ['option']

def test_reactive_html_templated_variable_not_in_declared_node():
    with pytest.raises(ValueError) as excinfo:
        class TestTemplatedChildren(ReactiveHTML):

            children = param.List(default=[])

            _template = """
            <select>
            {%- for option in children %}
            <option id="option">{{option   }}</option>
            {%- endfor %}
            </select>
            """
    assert 'could not be expanded because the <select> node' in str(excinfo)
    assert '{%- for option in children %}' in str(excinfo)

def test_reactive_design_stylesheets_update(document, comm):
    widget = TextInput(stylesheets=[':host { --design-background-color: red }'])

    model = widget.get_root(document, comm)

    assert len(model.stylesheets) == 5
    assert model.stylesheets[-1] == widget.stylesheets[0]

    widget.stylesheets = [':host { --design-background-color: blue }']

    assert len(model.stylesheets) == 5
    assert model.stylesheets[-1] == widget.stylesheets[0]


def test_reactive_attribute_no_name(document, comm):
    # Regression: https://github.com/holoviz/panel/pull/7655
    class CustomComponent2(ReactiveHTML):
        groups = param.ListSelector(default=["A"], objects=["A", "B"])
        _scripts = {"groups": "console.log(data.groups)"}

    component = CustomComponent2()
    component.get_root(document, comm)
    # Should not error out
    component.groups = []
