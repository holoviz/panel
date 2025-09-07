import numpy as np
import pandas as pd
import pytest

from panel.layout import GridBox, Row
from panel.pane import panel
from panel.tests.util import mpl_available
from panel.widgets import (
    AutocompleteInput, ColorMap, CrossSelector, DiscreteSlider, MultiChoice,
    MultiSelect, NestedSelect, Select, ToggleGroup,
)


@pytest.mark.parametrize('widget', [AutocompleteInput, Select])
def test_list_constructor(widget):
    select = widget(options=['A', 1], value=1)
    assert select.options == ['A', 1]

@pytest.mark.parametrize('widget', [AutocompleteInput, Select])
def test_select_float_option_with_equality(widget):
    opts = {'A': 3.14, '1': 2.0}
    select = widget(options=opts, value=3.14, name='Select')
    assert select.value == 3.14

    select.value = 2
    assert select.value == 2.0

    select.value = 3.14
    assert select.value == 3.14

@pytest.mark.parametrize('widget', [AutocompleteInput, Select])
def test_select_text_option_with_equality(widget):
    opts = {'A': 'ABC', '1': 'DEF'}
    select = widget(options=opts, value='DEF', name='Select')
    assert select.value == 'DEF'

    select.value = 'ABC'
    assert select.value == 'ABC'

    select.value = 'DEF'
    assert select.value == 'DEF'

def test_select_from_list(document, comm):
    select = Select.from_values(['A', 'B', 'A', 'B', 'C'])

    assert select.options == ['A', 'B', 'C']
    assert select.value == 'A'

def test_select_from_array(document, comm):
    select = Select.from_values(np.array(['A', 'B', 'A', 'B', 'C']))

    assert select.options == ['A', 'B', 'C']
    assert select.value == 'A'

def test_select_from_index(document, comm):
    select = Select.from_values(pd.Index(['A', 'B', 'A', 'B', 'C'], name='index'))

    assert select.options == ['A', 'B', 'C']
    assert select.value == 'A'
    assert select.name == 'index'

def test_select_from_series(document, comm):
    select = Select.from_values(pd.Series(['A', 'B', 'A', 'B', 'C'], name='Series'))

    assert select.options == ['A', 'B', 'C']
    assert select.value == 'A'
    assert select.name == 'Series'

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

def test_autocomplete(document, comm):
    opts = {'A': 'a', '1': 1}
    select = AutocompleteInput(options=opts, value=opts['1'], name='Autocomplete')

    widget = select.get_root(document, comm=comm)

    assert isinstance(widget, select._widget_type)
    assert widget.title == 'Autocomplete'
    assert widget.value == str(opts['1'])
    assert widget.completions == list(opts)

    select._process_events({'value': 'A'})
    assert select.value == 'a'

    widget.value = '1'
    select.value = opts['1']
    assert select.value == opts['1']

    select.value = opts['A']
    assert widget.value == 'A'

def test_autocomplete_unrestricted(document, comm):
    opts = {'A': 'a', '1': 1}
    select = AutocompleteInput(options=opts, value=opts['1'], name='Autocomplete', restrict=False)

    widget = select.get_root(document, comm=comm)

    assert isinstance(widget, select._widget_type)
    assert widget.title == 'Autocomplete'
    assert widget.value == str(opts['1'])
    assert widget.completions == list(opts)

    select._process_events({'value': str(opts['A'])})
    assert select.value == opts['A']

    select._process_events({'value': 'foo'})
    assert select.value == 'foo'

    select.value = 'bar'
    assert widget.value == 'bar'

def test_autocomplete_restricted_reset_on_new_options(document, comm):
    opts = {'A': 'a', '1': 1}
    select = AutocompleteInput(options=opts, value=1, name='Autocomplete', restrict=True)

    widget = select.get_root(document, comm=comm)

    select.options = {'A': 'a', '2': 2}
    assert widget.value == ''

def test_autocomplete_unrestricted_no_reset_on_new_options(document, comm):
    opts = {'A': 'a', '1': 1}
    select = AutocompleteInput(options=opts, value=1, name='Autocomplete', restrict=False)

    widget = select.get_root(document, comm=comm)

    select.options = {'A': 'a', '2': 2}
    assert widget.value == '1'

@pytest.mark.parametrize('widget', [AutocompleteInput, Select])
def test_select_parameterized_option_labels(widget):
    c1 = panel("Value1", name="V1")
    c2 = panel("Value2")
    c3 = panel("Value3", name="V3")

    select = widget(options=[c1, c2, c3], value=c1)
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
    assert select.value is None
    assert widget.value is None


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

@pytest.mark.parametrize('widget', [AutocompleteInput, Select])
def test_select_change_options(widget, document, comm):
    opts = {'A': 'a', '1': 1}
    select = widget(options=opts, value=opts['1'], name='Select')

    widget = select.get_root(document, comm=comm)

    select.options = {'A': 'a'}
    assert select.value == ('' if select._allows_none else opts['A'])
    assert widget.value == (str(opts['A']) if select._allows_values else '')

    select.options = {}
    assert select.value is select.param['value'].default
    assert widget.value == select.param['value'].default

@pytest.mark.parametrize('widget', [AutocompleteInput, Select])
def test_select_non_hashable_options(widget, document, comm):
    opts = {'A': np.array([1, 2, 3]), '1': np.array([3, 4, 5])}
    select = widget(options=opts, value=opts['1'], name='Select')

    widget = select.get_root(document, comm=comm)

    select.value = opts['A']
    assert select.value is opts['A']
    assert widget.value == (str(opts['A']) if select._allows_values else 'A')

    opts.pop('A')
    select.options = opts
    assert select.value is ('' if select._allows_none else opts['1'])
    assert widget.value == (str(opts['1']) if select._allows_values else '')

def test_select_mutables(document, comm):
    opts = {'A': [1,2,3], 'B': [2,4,6], 'C': dict(a=1,b=2)}
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
    select = Select(options={'A': 'A', '1': 1, 'C': object},
                    value='A', name='Select')

    def set_options(event):
        if event.new == 1:
            select.options = {'D': 2, 'E': 'a'}
    select.param.watch(set_options, 'value')

    model = select.get_root(document, comm=comm)

    select.value = 1
    assert model.value == str(list(select.options.values())[0])
    assert model.options == [(str(v),k) for k,v in select.options.items()]


def test_nested_select_defaults(document, comm):
    options = {
        "Andrew": {
            "temp": [1000, 925, 700, 500, 300],
            "vorticity": [500, 300],
        },
        "Ben": {
            "temp": [500, 300],
            "windspeed": [700, 500, 300],
        },
    }
    select = NestedSelect(options=options)
    assert select.value == {2: 1000, 0: 'Andrew', 1: 'temp'}
    assert select.options == options
    assert select.levels == []
    assert select._max_depth == 3


def test_nested_select_from_multi_index(df_multiindex):
    select = NestedSelect.from_values(df_multiindex.index)

    assert select.options == {
        'group0': ['subgroup0', 'subgroup1'],
        'group1': ['subgroup0', 'subgroup1'],
    }
    assert select.value == {'groups': 'group0', 'subgroups': 'subgroup0'}
    assert select._max_depth == 2
    assert select.levels == ['groups', 'subgroups']

def test_nested_select_from_index():
    select = NestedSelect.from_values(pd.Index(['A', 'B', 'A', 'B', 'C'], name='index'))

    assert select.options == ['A', 'B', 'C']
    assert select.value == {'index': 'A'}
    assert select._max_depth == 1

def test_nested_select_from_series():
    select = NestedSelect.from_values(pd.Series(['A', 'B', 'A', 'B', 'C'], name='Series'))

    assert select.options == ['A', 'B', 'C']
    assert select.value == {'Series': 'A'}
    assert select._max_depth == 1

def test_nested_select_init_value(document, comm):
    options = {
        "Andrew": {
            "temp": [1000, 925, 700, 500, 300],
            "vorticity": [500, 300],
        },
        "Ben": {
            "temp": [500, 300],
            "windspeed": [700, 500, 300],
        },
    }
    value = {2: 1000, 0: 'Andrew', 1: 'temp'}
    select = NestedSelect(options=options, value=value)
    assert select.value == value
    assert select.options == options
    assert select.levels == []


def test_nested_select_init_empty(document, comm):
    #with pytest.raises(Exception):
    select = NestedSelect()
    assert select.value is None
    assert select.options is None
    assert select.levels == []

def test_nested_select_max_depth_empty_first_sublevel(document, comm):
    select = NestedSelect(options={'foo': ['a', 'b'], 'bar': []})

    assert select._max_depth == 2

def test_nested_select_max_depth_empty_second_sublevel(document, comm):
    select = NestedSelect(options={'foo': {'0': ['a', 'b'], '1': []}, 'bar': {'0': []}})

    assert select._max_depth == 3

def test_nested_select_init_levels(document, comm):
    options = {
        "Andrew": {
            "temp": [1000, 925, 700, 500, 300],
            "vorticity": [500, 300],
        },
        "Ben": {
            "temp": [500, 300],
            "windspeed": [700, 500, 300],
        },
    }
    levels = ["Name", "Var", "Level"]
    select = NestedSelect(options=options, levels=levels)
    assert select.value == {'Level': 1000, 'Name': 'Andrew', 'Var': 'temp'}
    assert select.options == options
    assert select.levels == levels


def test_nested_select_update_options(document, comm):
    options = {
        "Andrew": {
            "temp": [1000, 925, 700, 500, 300],
            "vorticity": [500, 300],
        },
        "Ben": {
            "temp": [500, 300],
            "windspeed": [700, 500, 300],
        },
    }
    levels = ["Name", "Var", "Level"]
    value = {'Level': 1000, 'Name': 'Andrew', 'Var': 'temp'}
    select = NestedSelect(options=options, levels=levels, value=value)
    options = {
        "August": {
            "temp": [500, 300],
        }
    }
    select.options = options
    assert select.options == options
    assert select.value == {'Level': 500, 'Name': 'August', 'Var': 'temp'}
    assert select.levels == levels


def test_nested_select_update_value(document, comm):
    options = {
        "Andrew": {
            "temp": [1000, 925, 700, 500, 300],
            "vorticity": [500, 300],
        },
        "Ben": {
            "temp": [500, 300],
            "windspeed": [700, 500, 300],
        },
    }
    levels = ["Name", "Var", "Level"]
    value = {'Name': 'Ben', 'Var': 'temp', 'Level': 300}
    select = NestedSelect(options=options, levels=levels, value=value)
    value = {'Name': 'Ben', 'Var': 'windspeed', 'Level': 700}
    select.value = value
    assert select.options == options
    assert select.value == value
    assert select.levels == levels


def test_nested_select_update_value_invalid(document, comm):
    options = {
        "Andrew": {
            "temp": [1000, 925, 700, 500, 300],
            "vorticity": [500, 300],
        },
        "Ben": {
            "temp": [500, 300],
            "windspeed": [700, 500, 300],
        },
    }
    levels = ["Name", "Var", "Level"]
    value = {'Name': 'Ben', 'Var': 'temp', 'Level': 300}
    select = NestedSelect(options=options, levels=levels, value=value)
    value = {'Name': 'Ben', 'Var': 'windspeed', 'Level': 123456}
    with pytest.raises(ValueError, match="Failed to set value"):
        select.value = value


def test_nested_select_update_levels(document, comm):
    options = {
        "Andrew": {
            "temp": [1000, 925, 700, 500, 300],
            "vorticity": [500, 300],
        },
        "Ben": {
            "temp": [500, 300],
            "windspeed": [700, 500, 300],
        },
    }
    value = {'Name': 'Ben', 'Var': 'temp', 'Level': 300}
    select = NestedSelect(options=options, levels=["Name", "Var", "Level"], value=value)
    levels = ["user", "wx_var", "lev"]
    select.levels = levels
    assert select.options == options
    assert select.value == {'user': 'Ben', 'wx_var': 'temp', 'lev': 300}
    assert select.levels == levels


def test_nested_select_update_levels_invalid(document, comm):
    options = {
        "Andrew": {
            "temp": [1000, 925, 700, 500, 300],
            "vorticity": [500, 300],
        },
        "Ben": {
            "temp": [500, 300],
            "windspeed": [700, 500, 300],
        },
    }
    value = {'Name': 'Ben', 'Var': 'temp', 'Level': 300}
    select = NestedSelect(options=options, levels=["Name", "Var", "Level"], value=value)
    levels = ["user", "wx_var", "lev", "abc"]
    with pytest.raises(ValueError, match="must be of length 3"):
        select.levels = levels

def test_nested_select_update_all(document, comm):
    options = {
        "Andrew": {
            "temp": [1000, 925, 700, 500, 300],
            "vorticity": [500, 300],
        },
        "Ben": {
            "temp": [500, 300],
            "windspeed": [700, 500, 300],
        },
    }
    value = {'Name': 'Ben', 'Var': 'temp', 'Level': 300}
    select = NestedSelect(options=options, levels=["Name", "Var", "Level"], value=value)
    new_levels = ["N", "V", "L"]
    new_options = {
        "Ben": {
            "temp": [500, 300],
            "windspeed": [1000],
        }
    }
    new_value = {'N': 'Ben', 'V': 'windspeed', 'L': 1000}
    select.param.update(
        options=new_options,
        levels=new_levels,
        value=new_value
    )
    assert select.options == new_options
    assert select.value == new_value
    assert select.levels == new_levels


def test_nested_select_disabled(document, comm):
    options = {
        "Andrew": {
            "temp": [1000, 925, 700, 500, 300],
            "vorticity": [500, 300],
        },
    }
    select = NestedSelect(options=options, levels=["Name", "Var", "Level"])
    select.disabled = True
    assert select._widgets[0].disabled

    select.disabled = False
    assert not select._widgets[0].disabled


def test_nested_select_partial_options_init(document, comm):
    options = {
        "Ben": {},
        "Andrew": {
            "temp": [1000, 925, 700, 500, 300],
            "vorticity": [500, 300],
        },
    }
    levels = ["Name", "Var", "Level"]
    select = NestedSelect(
        options=options,
        levels=levels,
    )
    assert select._widgets[0].value == 'Ben'
    assert select._widgets[1].value is None
    assert select._widgets[2].value is None
    assert select._widgets[0].visible
    assert not select._widgets[1].visible
    assert not select._widgets[2].visible
    assert select.value == {'Name': 'Ben', 'Var': None, 'Level': None}


def test_nested_select_partial_options_set(document, comm):
    options = {
        "Andrew": {
            "temp": [1000, 925, 700, 500, 300],
            "vorticity": [500, 300],
        },
    }
    select = NestedSelect(options=options)
    select.options = {"Ben": []}
    assert select._widgets[0].value == 'Ben'
    assert select._widgets[0].visible
    assert select.value == {0: 'Ben', 1: None}


def test_nested_select_partial_value_init(document, comm):
    options = {
        "Andrew": {
            "temp": [1000, 925, 700, 500, 300],
            "vorticity": [500, 300],
        },
        "Ben": {
            "temp": [500, 300],
            "windspeed": [700, 500, 300],
        },
    }
    levels = ["Name", "Var", "Level"]
    select = NestedSelect(
        options=options,
        levels=levels,
        value={'Name': 'Ben'}
    )
    assert select._widgets[0].value == 'Ben'
    assert select._widgets[1].value == "temp"
    assert select._widgets[2].value == 500
    assert select._widgets[0].visible
    assert select._widgets[1].visible
    assert select._widgets[2].visible
    assert select.value == {'Name': 'Ben', 'Var': 'temp', 'Level': 500}


def test_nested_select_partial_value_set(document, comm):
    options = {
        "Andrew": {
            "temp": [1000, 925, 700, 500, 300],
            "vorticity": [500, 300],
        },
        "Ben": {
            "temp": [500, 300],
            "windspeed": [700, 500, 300],
        },
    }
    levels = ["Name", "Var", "Level"]
    select = NestedSelect(
        options=options,
        levels=levels,
    )
    select.value = {'Name': 'Ben'}
    assert select.value == {'Name': 'Ben', 'Var': 'temp', 'Level': 500}


def test_nested_select_custom_widgets(document, comm):
    options = {
        "Andrew": {
            "temp": [1000, 925, 700, 500, 300],
            "vorticity": [500, 300],
        },
        "Ben": {
            "temp": [500, 300],
            "windspeed": [700, 500, 300],
        },
    }
    select = NestedSelect(
        options=options,
        levels=[
            {"name": "Name", "type": Select, "width": 250},
            {"name": "Variable", "type": Select},
            {"name": "lvl", "type": DiscreteSlider},
        ],
    )
    widget_0 = select._widgets[0]
    widget_1 = select._widgets[1]
    widget_2 = select._widgets[2]
    assert isinstance(widget_0, Select)
    assert isinstance(widget_1, Select)
    assert isinstance(widget_2, DiscreteSlider)
    assert widget_0.width == 250
    assert widget_0.name == "Name"
    assert widget_1.name == "Variable"
    assert widget_2.name == "lvl"
    assert widget_0.options == ["Andrew", "Ben"]
    assert widget_1.options == ["temp", "vorticity"]
    assert widget_2.options == [1000, 925, 700, 500, 300]


def test_nested_select_callable_top_level(document, comm):
    def list_options(level, value):
        if level == "time_step":
            options = {"Daily": list_options, "Monthly": list_options}
        elif level == "level_type":
            options = {f"{value['time_step']}_upper": list_options, f"{value['time_step']}_lower": list_options}
        else:
            options = [f"{value['level_type']}.json", f"{value['level_type']}.csv"]

        return options

    select = NestedSelect(
        options=list_options,
        levels=["time_step", "level_type", "file"],
    )
    assert select._widgets[0].options == ["Daily", "Monthly"]
    assert select._widgets[1].options == ["Daily_upper", "Daily_lower"]
    assert select._widgets[2].options == ["Daily_upper.json", "Daily_upper.csv"]
    assert select.value == {"time_step": "Daily", "level_type": "Daily_upper", "file": "Daily_upper.json"}
    assert select._max_depth == 3

    select.value = {"time_step": "Monthly"}
    assert select._widgets[0].options == ["Daily", "Monthly"]
    assert select._widgets[1].options == ["Monthly_upper", "Monthly_lower"]
    assert select._widgets[2].options == ["Monthly_upper.json", "Monthly_upper.csv"]
    assert select.value == {"time_step": "Monthly", "level_type": "Monthly_upper", "file": "Monthly_upper.json"}
    assert select._max_depth == 3


def test_nested_select_callable_mid_level(document, comm):
    def list_options(level, value):
        if level == "level_type":
            options = {f"{value['time_step']}_upper": list_options, f"{value['time_step']}_lower": list_options}
        else:
            options = [f"{value['level_type']}.json", f"{value['level_type']}.csv"]

        return options

    select = NestedSelect(
        options={"Daily": list_options, "Monthly": list_options},
        levels=["time_step", "level_type", "file"],
    )
    assert select._widgets[0].options == ["Daily", "Monthly"]
    assert select._widgets[1].options == ["Daily_upper", "Daily_lower"]
    assert select._widgets[2].options == ["Daily_upper.json", "Daily_upper.csv"]
    assert select.value == {"time_step": "Daily", "level_type": "Daily_upper", "file": "Daily_upper.json"}
    assert select._max_depth == 3

    select.value = {"time_step": "Monthly"}
    assert select._widgets[0].options == ["Daily", "Monthly"]
    assert select._widgets[1].options == ["Monthly_upper", "Monthly_lower"]
    assert select._widgets[2].options == ["Monthly_upper.json", "Monthly_upper.csv"]
    assert select.value == {"time_step": "Monthly", "level_type": "Monthly_upper", "file": "Monthly_upper.json"}
    assert select._max_depth == 3


def test_nested_select_dynamic_levels(document, comm):
    select = NestedSelect(
        options={
            "Easy": {"Easy_A": {}, "Easy_B": {}},
            "Medium": {
                "Medium_A": {},
                "Medium_B": {"Medium_B_1": []},
                "Medium_C": {
                    "Medium_C_1": ["Medium_C_1_1"],
                    "Medium_C_2": ["Medium_C_2_1", "Medium_C_2_2"],
                },
            },
            "Hard": {}
        },
        levels=["A", "B", "C", "D"],
    )
    assert select._widgets[0].visible
    assert select._widgets[1].visible
    assert not select._widgets[2].visible
    assert not select._widgets[3].visible

    assert select._widgets[0].options == ["Easy", "Medium", "Hard"]
    assert select._widgets[1].options == ["Easy_A", "Easy_B"]
    assert select._widgets[2].options == []
    assert select._widgets[3].options == []

    assert select.value == {"A": "Easy", "B": "Easy_A", "C": None, "D": None}

    # now update to Medium
    select.value = {"A": "Medium", "B": "Medium_C"}
    assert select._widgets[0].visible
    assert select._widgets[1].visible
    assert select._widgets[2].visible
    assert select._widgets[3].visible

    assert select._widgets[0].options == ["Easy", "Medium", "Hard"]
    assert select._widgets[1].options == ["Medium_A", "Medium_B", "Medium_C"]
    assert select._widgets[2].options == ["Medium_C_1", "Medium_C_2"]
    assert select._widgets[3].options == ["Medium_C_1_1"]

    assert select.value == {"A": "Medium", "B": "Medium_C", "C": "Medium_C_1", "D": "Medium_C_1_1"}

    # now update to Hard
    select.value = {"A": "Hard"}
    assert select._widgets[0].visible
    assert not select._widgets[1].visible
    assert not select._widgets[2].visible
    assert not select._widgets[3].visible

    assert select._widgets[0].options == ["Easy", "Medium", "Hard"]
    assert select._widgets[1].options == []
    assert select._widgets[2].options == []
    assert select._widgets[3].options == []

    assert select.value == {"A": "Hard", "B": None, "C": None, "D": None}


def test_nested_select_callable_must_have_levels(document, comm):
    def list_options(level, value):
        pass

    with pytest.raises(ValueError, match="levels must be specified"):
        NestedSelect(
            options={"Daily": list_options, "Monthly": list_options},
        )


def test_nested_select_layout_listlike(document, comm):
    options = {
        "Andrew": {
            "temp": [1000, 925, 700, 500, 300],
            "vorticity": [500, 300],
        },
        "Ben": {
            "temp": [500, 300],
            "windspeed": [700, 500, 300],
        },
    }
    select = NestedSelect(
        options=options,
        layout=Row,
    )
    assert isinstance(select._composite, Row)


def test_nested_select_layout_dict(document, comm):
    options = {
        "Andrew": {
            "temp": [1000, 925, 700, 500, 300],
            "vorticity": [500, 300],
        },
        "Ben": {
            "temp": [500, 300],
            "windspeed": [700, 500, 300],
        },
    }
    select = NestedSelect(
        options=options,
        layout={"type": GridBox, "ncols": 2},
    )
    assert isinstance(select._composite[0], GridBox)
    assert select._composite[0].ncols == 2


def test_nested_select_layout_dynamic_update(document, comm):
    options = {
        "Andrew": {
            "temp": [1000, 925, 700, 500, 300],
            "vorticity": [500, 300],
        },
        "Ben": {
            "temp": [500, 300],
            "windspeed": [700, 500, 300],
        },
    }
    select = NestedSelect(
        options=options,
        layout={"type": GridBox, "ncols": 2},
    )
    assert isinstance(select._composite[0], GridBox)
    assert select._composite[0].ncols == 2

    select.layout = Row
    assert isinstance(select._composite, Row)


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
    select.param.update(value=20, disabled_options=[10])

    widget = select.get_root(document, comm=comm)

    assert widget.value == '20'
    assert select.value == 20
    assert widget.disabled_options == [10]


def test_multi_select_from_list():
    select = MultiSelect.from_values(['A', 'B', 'A', 'B', 'C'])

    assert select.options == ['A', 'B', 'C']
    assert select.value == []

def test_multi_select_from_array():
    select = MultiSelect.from_values(np.array(['A', 'B', 'A', 'B', 'C']))

    assert select.options == ['A', 'B', 'C']
    assert select.value == []

def test_multi_select_from_index():
    select = MultiSelect.from_values(pd.Index(['A', 'B', 'A', 'B', 'C'], name='index'))

    assert select.options == ['A', 'B', 'C']
    assert select.value == []
    assert select.name == 'index'

def test_multi_select_from_series(document, comm):
    select = MultiSelect.from_values(pd.Series(['A', 'B', 'A', 'B', 'C'], name='Series'))

    assert select.options == ['A', 'B', 'C']
    assert select.value == []
    assert select.name == 'Series'

def test_multi_select(document, comm):
    select = MultiSelect(options={'A': 'A', '1': 1, 'C': object},
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
    choice = MultiChoice(options={'A': 'A', '1': 1, 'C': object},
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
    select = MultiSelect(options={'A': 'A', '1': 1, 'C': object},
                         value=[object, 1], name='Select')

    def set_options(event):
        if event.new == [1]:
            select.options = {'D': 2, 'E': 'a'}
    select.param.watch(set_options, 'value')

    model = select.get_root(document, comm=comm)

    select.value = [1]
    assert model.value == []
    assert model.options == ['D', 'E']


def test_toggle_group_error_init(document, comm):
    with pytest.raises(ValueError):
        ToggleGroup(options={'A': 'A', '1': 1, 'C': object},
                    value=1, name='RadioButtonGroup',
                    widget_type='button', behavior='check')

    with pytest.raises(ValueError):
        ToggleGroup(options={'A': 'A', '1': 1, 'C': object},
                    value=[1, object], name='RadioButtonGroup',
                    widget_type='button', behavior='radio')

    with pytest.raises(ValueError):
        ToggleGroup(options={'A': 'A', '1': 1, 'C': object},
                    value=[1, object], name='RadioButtonGroup',
                    widget_type='buttons')

    with pytest.raises(ValueError):
        ToggleGroup(options={'A': 'A', '1': 1, 'C': object},
                    value=[1, object], name='RadioButtonGroup',
                    behavior='checks')


def test_toggle_group_check(document, comm):

    for widget_type in ToggleGroup._widgets_type:
        select = ToggleGroup(options={'A': 'A', '1': 1, 'C': object},
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
        select = ToggleGroup(options={'A': 'A', '1': 1, 'C': object},
                             value=1, name='RadioButtonGroup',
                             widget_type=widget_type, behavior='radio')

        widget = select.get_root(document, comm=comm)

        assert isinstance(widget, select._widget_type)
        assert widget.active == 1
        assert widget.labels == ['A', '1', 'C']

        widget.active = 2
        select._process_events({'active': 2})
        assert select.value is object

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
    cross_select._search[False].value_input = 'D'
    assert cross_select._lists[False].value == ['D']

    # Move queried item
    cross_select._buttons[True].param.trigger('clicks')
    assert cross_select._lists[False].options == ['4']
    assert cross_select._lists[False].value == []
    assert cross_select._lists[True].options == ['D']
    assert cross_select._lists[False].value == []

    # Query selected item
    cross_select._search[True].value_input = 'D'
    cross_select._buttons[False].param.trigger('clicks')
    assert cross_select._lists[False].options == ['D', '4']
    assert cross_select._lists[False].value == ['D']
    assert cross_select._lists[True].options == []

    # Clear query
    cross_select._search[False].value_input = ''
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

def test_colormap_set_value_name(document, comm):
    color_map = ColorMap(options={'A': ['#ff0', '#0ff'], 'B': ['#00f', '#f00']}, value=['#00f', '#f00'])

    model = color_map.get_root(document, comm=comm)

    assert model.value == 'B'
    assert color_map.value_name == 'B'

    color_map.value = ['#ff0', '#0ff']

    assert model.value == 'A'
    assert color_map.value_name == 'A'

def test_colormap_set_value(document, comm):
    color_map = ColorMap(options={'A': ['#ff0', '#0ff'], 'B': ['#00f', '#f00']}, value_name='B')

    model = color_map.get_root(document, comm=comm)

    assert model.value == 'B'
    assert color_map.value == ['#00f', '#f00']

    color_map.value_name = 'A'

    assert model.value == 'A'
    assert color_map.value == ['#ff0', '#0ff']

@mpl_available
def test_colormap_mpl_cmap(document, comm):
    from matplotlib.cm import Set1, tab10
    color_map = ColorMap(options={'tab10': tab10, 'Set1': Set1}, value_name='Set1')

    model = color_map.get_root(document, comm=comm)

    assert model.items == [
        ('tab10', [
            'rgba(31, 119, 180, 1)',
            'rgba(255, 127, 14, 1)',
            'rgba(44, 160, 44, 1)',
            'rgba(214, 39, 40, 1)',
            'rgba(148, 103, 189, 1)',
            'rgba(140, 86, 75, 1)',
            'rgba(227, 119, 194, 1)',
            'rgba(127, 127, 127, 1)',
            'rgba(188, 189, 34, 1)',
            'rgba(23, 190, 207, 1)'
        ]),
        ('Set1', [
            'rgba(228, 26, 28, 1)',
            'rgba(55, 126, 184, 1)',
            'rgba(77, 175, 74, 1)',
            'rgba(152, 78, 163, 1)',
            'rgba(255, 127, 0, 1)',
            'rgba(255, 255, 51, 1)',
            'rgba(166, 86, 40, 1)',
            'rgba(247, 129, 191, 1)',
            'rgba(153, 153, 153, 1)'
        ])
    ]
