from collections import OrderedDict

import numpy as np
import pytest

from panel.pane import panel
from panel.widgets import (
    CrossSelector, MultiChoice, MultiSelect, Select, ToggleGroup,
)


def test_select_list_constructor():
    select = Select(options=['A', 1], value=1)
    assert select.options == ['A', 1]


def test_select_float_option_with_equality():
    opts = {'A': 3.14, '1': 2.0}
    select = Select(options=opts, value=3.14, name='Select')
    assert select.value == 3.14

    select.value = 2
    assert select.value == 2.0

    select.value = 3.14
    assert select.value == 3.14


def test_select_text_option_with_equality():
    opts = {'A': 'ABC', '1': 'DEF'}
    select = Select(options=opts, value='DEF', name='Select')
    assert select.value == 'DEF'

    select.value = 'ABC'
    assert select.value == 'ABC'

    select.value = 'DEF'
    assert select.value == 'DEF'


def test_select(document, comm):
    opts = {'A': 'a', '1': 1}
    select = Select(options=opts, value=opts['1'], name='Select')

    widget = select.get_root(document, comm=comm)

    assert isinstance(widget, select._widget_type)
    assert widget.title == 'Select'
    assert widget.value == str(opts['1'])
    assert widget.options == [(str(v),k) for k,v in opts.items()]

    select._process_events({'value': str(opts['A'])})
    assert select.value == opts['A']

    widget.value = str(opts['1'])
    select.value = opts['1']
    assert select.value == opts['1']

    select.value = opts['A']
    assert widget.value == str(opts['A'])


def test_select_parameterized_option_labels():
    c1 = panel("Value1", name="V1")
    c2 = panel("Value2")
    c3 = panel("Value3", name="V3")

    select = Select(options=[c1, c2, c3], value=c1)
    assert select.labels == ['V1', 'Markdown(str)', 'V3']


def test_select_groups_list_options(document, comm):
    groups = dict(a=[1, 2], b=[3])
    select = Select(value=groups['a'][0], groups=groups, name='Select')

    widget = select.get_root(document, comm=comm)

    assert isinstance(widget, select._widget_type)
    assert widget.title == 'Select'
    assert widget.value == str(groups['a'][0])
    assert widget.options == {gr: [(str(v), str(v)) for v in values] for gr, values in groups.items()}

    select._process_events({'value': str(groups['a'][1])})
    assert select.value == groups['a'][1]

    select._process_events({'value': str(groups['a'][0])})
    assert select.value == groups['a'][0]

    select.value = groups['a'][1]
    assert widget.value == str(groups['a'][1])


def test_select_groups_dict_options(document, comm):
    groups = dict(A=dict(a=1, b=2), B=dict(c=3))
    select = Select(value=groups['A']['a'], groups=groups, name='Select')

    widget = select.get_root(document, comm=comm)

    assert isinstance(widget, select._widget_type)
    assert widget.title == 'Select'
    assert widget.value == str(groups['A']['a'])
    assert widget.options == {'A': [('1', 'a'), ('2', 'b')], 'B': [('3', 'c')]}

    select._process_events({'value': str(groups['B']['c'])})
    assert select.value == groups['B']['c']

    select._process_events({'value': str(groups['A']['b'])})
    assert select.value == groups['A']['b']

    select.value = groups['A']['a']
    assert widget.value == str(groups['A']['a'])


def test_select_change_groups(document, comm):
    groups = dict(A=dict(a=1, b=2), B=dict(c=3))
    select = Select(value=groups['A']['a'], groups=groups, name='Select')

    widget = select.get_root(document, comm=comm)

    new_groups = dict(C=dict(d=4), D=dict(e=5, f=6))
    select.groups = new_groups
    assert select.value == new_groups['C']['d']
    assert widget.value == str(new_groups['C']['d'])
    assert widget.options == {'C': [('4', 'd')], 'D': [('5', 'e'), ('6', 'f')]}

    select.groups = {}
    assert select.value == None
    assert widget.value == ''


def test_select_groups_error_with_options():
    # Instantiate with groups and options
    with pytest.raises(ValueError):
        Select(options=[1, 2], groups=dict(a=[1], b=[2]), name='Select')

    opts = [1, 2, 3]
    groups = dict(a=[1, 2], b=[3])

    # Instamtiate with options and then update groups
    select = Select(options=opts, name='Select')
    with pytest.raises(ValueError):
        select.groups = groups

    # Instantiate with groups and then update options
    select = Select(groups=groups, name='Select')
    with pytest.raises(ValueError):
        select.options = opts


def test_select_change_options(document, comm):
    opts = {'A': 'a', '1': 1}
    select = Select(options=opts, value=opts['1'], name='Select')

    widget = select.get_root(document, comm=comm)

    select.options = {'A': 'a'}
    assert select.value == opts['A']
    assert widget.value == str(opts['A'])

    select.options = {}
    assert select.value == None
    assert widget.value == ''


def test_select_non_hashable_options(document, comm):
    opts = {'A': np.array([1, 2, 3]), '1': np.array([3, 4, 5])}
    select = Select(options=opts, value=opts['1'], name='Select')

    widget = select.get_root(document, comm=comm)

    select.value = opts['A']
    assert select.value is opts['A']
    assert widget.value == str(opts['A'])

    opts.pop('A')
    select.options = opts
    assert select.value is opts['1']
    assert widget.value == str(opts['1'])


def test_select_mutables(document, comm):
    opts = OrderedDict([('A', [1,2,3]), ('B', [2,4,6]), ('C', dict(a=1,b=2))])
    select = Select(options=opts, value=opts['B'], name='Select')

    widget = select.get_root(document, comm=comm)

    assert isinstance(widget, select._widget_type)
    assert widget.title == 'Select'
    assert widget.value == str(opts['B'])
    assert widget.options == [(str(v),k) for k,v in opts.items()]

    widget.value = str(opts['B'])
    select._process_events({'value': str(opts['A'])})
    assert select.value == opts['A']

    widget.value = str(opts['B'])
    select._process_events({'value': str(opts['B'])})
    assert select.value == opts['B']

    select.value = opts['A']
    assert widget.value == str(opts['A'])


def test_select_change_options_on_watch(document, comm):
    select = Select(options=OrderedDict([('A', 'A'), ('1', 1), ('C', object)]),
                         value='A', name='Select')

    def set_options(event):
        if event.new == 1:
            select.options = OrderedDict([('D', 2), ('E', 'a')])
    select.param.watch(set_options, 'value')

    model = select.get_root(document, comm=comm)

    select.value = 1
    assert model.value == str(list(select.options.values())[0])
    assert model.options == [(str(v),k) for k,v in select.options.items()]


@pytest.mark.parametrize('options', [[10, 20], dict(A=10, B=20)], ids=['list', 'dict'])
@pytest.mark.parametrize('size', [1, 2], ids=['size=1', 'size>1'])
def test_select_disabled_options_init(options, size, document, comm):
    select = Select(options=options, disabled_options=[20], size=size)

    widget = select.get_root(document, comm=comm)

    assert isinstance(widget, select._widget_type)
    assert widget.disabled_options == [20]


@pytest.mark.parametrize('options', [[10, 20], dict(A=10, B=20)], ids=['list', 'dict'])
@pytest.mark.parametrize('size', [1, 2], ids=['size=1', 'size>1'])
def test_select_disabled_options_after_init(options, size, document, comm):
    select = Select(options=options, size=size)
    select.disabled_options = [20]

    widget = select.get_root(document, comm=comm)

    assert isinstance(widget, select._widget_type)
    assert widget.disabled_options == [20]


@pytest.mark.parametrize('options', [[10, 20], dict(A=10, B=20)], ids=['list', 'dict'])
@pytest.mark.parametrize('size', [1, 2], ids=['size=1', 'size>1'])
def test_select_disabled_options_error_on_init(options, size):
    with pytest.raises(ValueError, match='as it is one of the disabled options'):
        Select(options=options, disabled_options=[10])


@pytest.mark.parametrize('options', [[10, 20], dict(A=10, B=20)], ids=['list', 'dict'])
@pytest.mark.parametrize('size', [1, 2], ids=['size=1', 'size>1'])
def test_select_disabled_options_all_raises_error_on_init(options, size):
    with pytest.raises(ValueError, match='All the options'):
        Select(options=options, disabled_options=[10, 20], size=size)


@pytest.mark.parametrize('options', [[10, 20], dict(A=10, B=20)], ids=['list', 'dict'])
@pytest.mark.parametrize('size', [1, 2], ids=['size=1', 'size>1'])
def test_select_disabled_options_all_raises_error_after_init(options, size):
    select = Select(options=options, size=size)

    with pytest.raises(ValueError, match='All the options'):
        select.disabled_options = [10, 20]


@pytest.mark.parametrize('options', [[10, 20], dict(A=10, B=20)], ids=['list', 'dict'])
@pytest.mark.parametrize('size', [1, 2], ids=['size=1', 'size>1'])
def test_select_disabled_options_error_disabled_options_not_in_options(options, size):
    with pytest.raises(ValueError, match='Cannot disable non existing options'):
        Select(options=options, disabled_options=[30], size=size)


@pytest.mark.parametrize('options', [[10, 20], dict(A=10, B=20)], ids=['list', 'dict'])
@pytest.mark.parametrize('size', [1, 2], ids=['size=1', 'size>1'])
def test_select_disabled_options_error_set_value(options, size):
    select = Select(options=options, disabled_options=[20], size=size)
    with pytest.raises(ValueError, match='as it is a disabled option'):
        select.value = 20


@pytest.mark.parametrize('options', [[10, 20], dict(A=10, B=20)], ids=['list', 'dict'])
@pytest.mark.parametrize('size', [1, 2], ids=['size=1', 'size>1'])
def test_select_disabled_options_error_set_disabled_options(options, size):
    select = Select(value=20, options=options, size=size)
    with pytest.raises(ValueError, match='Cannot set disabled_options'):
        select.disabled_options = [20]


@pytest.mark.parametrize('options', [[10, 20], dict(A=10, B=20)], ids=['list', 'dict'])
@pytest.mark.parametrize('size', [1, 2], ids=['size=1', 'size>1'])
def test_select_disabled_options_set_value_and_disabled_options(options, size, document, comm):
    select = Select(options=options, disabled_options=[20], size=size)
    select.param.set_param(value=20, disabled_options=[10])

    widget = select.get_root(document, comm=comm)

    assert widget.value == '20'
    assert select.value == 20
    assert widget.disabled_options == [10]


def test_multi_select(document, comm):
    select = MultiSelect(options=OrderedDict([('A', 'A'), ('1', 1), ('C', object)]),
                         value=[object, 1], name='Select')

    widget = select.get_root(document, comm=comm)

    assert isinstance(widget, select._widget_type)
    assert widget.title == 'Select'
    assert widget.value == ['C', '1']
    assert widget.options == ['A', '1', 'C']

    widget.value = ['1']
    select._process_events({'value': ['1']})
    assert select.value == [1]

    widget.value = ['A', 'C']
    select._process_events({'value': ['A', 'C']})
    assert select.value == ['A', object]

    select.value = [object, 'A']
    assert widget.value == ['C', 'A']


def test_multi_choice(document, comm):
    choice = MultiChoice(options=OrderedDict([('A', 'A'), ('1', 1), ('C', object)]),
                         value=[object, 1], name='MultiChoice')

    widget = choice.get_root(document, comm=comm)

    assert isinstance(widget, choice._widget_type)
    assert widget.title == 'MultiChoice'
    assert widget.value == ['C', '1']
    assert widget.options == ['A', '1', 'C']

    widget.value = ['1']
    choice._process_events({'value': ['1']})
    assert choice.value == [1]

    widget.value = ['A', 'C']
    choice._process_events({'value': ['A', 'C']})
    assert choice.value == ['A', object]

    choice.value = [object, 'A']
    assert widget.value == ['C', 'A']


def test_multi_select_change_options(document, comm):
    select = MultiSelect(options=OrderedDict([('A', 'A'), ('1', 1), ('C', object)]),
                         value=[object, 1], name='Select')

    def set_options(event):
        if event.new == [1]:
            select.options = OrderedDict([('D', 2), ('E', 'a')])
    select.param.watch(set_options, 'value')

    model = select.get_root(document, comm=comm)

    select.value = [1]
    assert model.value == []
    assert model.options == ['D', 'E']


def test_toggle_group_error_init(document, comm):
    with pytest.raises(ValueError):
        ToggleGroup(options=OrderedDict([('A', 'A'), ('1', 1), ('C', object)]),
                    value=1, name='RadioButtonGroup',
                    widget_type='button', behavior='check')

    with pytest.raises(ValueError):
        ToggleGroup(options=OrderedDict([('A', 'A'), ('1', 1), ('C', object)]),
                    value=[1, object], name='RadioButtonGroup',
                    widget_type='button', behavior='radio')

    with pytest.raises(ValueError):
        ToggleGroup(options=OrderedDict([('A', 'A'), ('1', 1), ('C', object)]),
                    value=[1, object], name='RadioButtonGroup',
                    widget_type='buttons')

    with pytest.raises(ValueError):
        ToggleGroup(options=OrderedDict([('A', 'A'), ('1', 1), ('C', object)]),
                    value=[1, object], name='RadioButtonGroup',
                    behavior='checks')


def test_toggle_group_check(document, comm):

    for widget_type in ToggleGroup._widgets_type:
        select = ToggleGroup(options=OrderedDict([('A', 'A'), ('1', 1), ('C', object)]),
                               value=[1, object], name='CheckButtonGroup',
                               widget_type=widget_type, behavior='check')

        widget = select.get_root(document, comm=comm)

        assert isinstance(widget, select._widget_type)
        assert widget.active == [1, 2]
        assert widget.labels == ['A', '1', 'C']

        widget.active = [2]
        select._process_events({'active': [2]})
        assert select.value == [object]

        widget.active = [0, 2]
        select._process_events({'active': [0, 2]})
        assert select.value == ['A', object]

        select.value = [object, 'A']
        assert widget.active == [2, 0]

        widget.active = []
        select._process_events({'active': []})
        assert select.value == []

        select.value = ["A", "B"]
        select.options = ["B", "C"]
        select.options = ["A", "B"]
        assert widget.labels[widget.active[0]] == "B"


def test_toggle_group_radio(document, comm):

    for widget_type in ToggleGroup._widgets_type:
        select = ToggleGroup(options=OrderedDict([('A', 'A'), ('1', 1), ('C', object)]),
                               value=1, name='RadioButtonGroup',
                               widget_type=widget_type, behavior='radio')

        widget = select.get_root(document, comm=comm)

        assert isinstance(widget, select._widget_type)
        assert widget.active == 1
        assert widget.labels == ['A', '1', 'C']

        widget.active = 2
        select._process_events({'active': 2})
        assert select.value == object

        select.value = 'A'
        assert widget.active == 0


def test_cross_select_constructor():
    cross_select = CrossSelector(options=['A', 'B', 'C', 1, 2, 3], value=['A', 1], size=5)

    assert cross_select._lists[True].options == ['A', '1']
    assert cross_select._lists[False].options == ['B', 'C', '2', '3']

    # Change selection
    cross_select.value = ['B', 2]
    assert cross_select._lists[True].options == ['B', '2']
    assert cross_select._lists[False].options == ['A', 'C', '1', '3']

    # Change options
    cross_select.options = {'D': 'D', '4': 4}
    assert cross_select._lists[True].options == []
    assert cross_select._lists[False].options == ['D', '4']

    # Change size
    cross_select.size = 5
    assert cross_select._lists[True].size == 5
    assert cross_select._lists[False].size == 5

    # Query unselected item
    cross_select._search[False].value = 'D'
    assert cross_select._lists[False].value == ['D']

    # Move queried item
    cross_select._buttons[True].param.trigger('clicks')
    assert cross_select._lists[False].options == ['4']
    assert cross_select._lists[False].value == []
    assert cross_select._lists[True].options == ['D']
    assert cross_select._lists[False].value == []

    # Query selected item
    cross_select._search[True].value = 'D'
    cross_select._buttons[False].param.trigger('clicks')
    assert cross_select._lists[False].options == ['D', '4']
    assert cross_select._lists[False].value == ['D']
    assert cross_select._lists[True].options == []

    # Clear query
    cross_select._search[False].value = ''
    assert cross_select._lists[False].value == []


def test_cross_select_move_selected_to_unselected():
    cross_select = CrossSelector(options=['A', 'B', 'C', 1, 2, 3], value=['A', 1], size=5)

    cross_select._lists[True].value = ['A', '1']
    cross_select._buttons[False].clicks = 1

    assert cross_select.value == []
    assert cross_select._lists[True].options == []


def test_cross_select_move_unselected_to_selected():
    cross_select = CrossSelector(options=['A', 'B', 'C', 1, 2, 3], value=['A', 1], size=5)

    cross_select._lists[False].value = ['B', '3']
    cross_select._buttons[True].clicks = 1

    assert cross_select.value == ['A', 1, 'B', 3]
    assert cross_select._lists[True].options == ['A', 'B', '1', '3']


def test_cross_select_move_unselected_to_selected_not_definition_order():
    cross_select = CrossSelector(options=['B', 'A', 'C', 1, 2, 3], value=['A', 1], size=5, definition_order=False)

    cross_select._lists[False].value = ['B', '3']
    cross_select._buttons[True].clicks = 1

    assert cross_select.value == ['A', 1, 'B', 3]
    assert cross_select._lists[True].options == ['A', '1', 'B', '3']
