import sys

from subprocess import check_output
from textwrap import dedent

import pytest


def test_no_blocklist_imports():
    check = """\
    import sys
    import panel

    blocklist = {"pandas", "bokeh.plotting", "panel_material_ui"}
    mods = blocklist & set(sys.modules)

    if mods:
        print(", ".join(mods), end="")
    """

    output = check_output([sys.executable, '-c', dedent(check)])

    assert output == b""


BLOCK_PANDAS = """\
import importlib.machinery
import sys

class BlockPandas:
    def find_spec(self, name, path=None, target=None):
        if name == 'pandas' or name.startswith('pandas.'):
            return importlib.machinery.ModuleSpec(name, self)

    def create_module(self, spec):
        raise ModuleNotFoundError(f'{spec.name} is blocked', name=spec.name)

    def exec_module(self, module):
        pass

sys.meta_path.insert(0, BlockPandas())
"""


def _run_without_pandas(code):
    output = check_output([sys.executable, '-c', BLOCK_PANDAS + dedent(code)])
    assert output.decode().strip().endswith('OK')


def test_tabulator_without_pandas():
    pytest.importorskip('polars')
    _run_without_pandas("""\
    import polars as pl
    import panel as pn

    from bokeh.document import Document
    from panel.models.tabulator import CellClickEvent, TableEditEvent

    for pagination in [None, 'remote']:
        table = pn.widgets.Tabulator(
            pl.DataFrame({'a': [3, 1, 2], 'b': ['x', 'Y', 'z']}),
            pagination=pagination, sorters=[{'field': 'a', 'dir': 'desc'}],
            filters=[{'field': 'b', 'type': 'like', 'value': ''}],
            header_filters=True, row_content=lambda row: row['b'],
        )
        table.get_root(Document())
        table.add_filter((1, None), 'a')
        table._process_events({'indices': [0]})
        table._process_event(TableEditEvent(model=None, column='b', row=0, value='Q', old='x'))
        table._process_events({'data': {'b': ['Q', 'z', 'Y'] if pagination else ['Q', 'Y', 'z']}})
        table._process_event(CellClickEvent(model=None, column='b', row=0))
        table._process_events({'expanded': [0]})
        table.stream({'a': [4], 'b': ['w']})
        table.patch({'a': [(0, 10)]})
        assert table.value.to_dicts()[0] == {'a': 10, 'b': 'Q'}, table.value
        assert table.selection == [0]
        assert len(table.current_view) == 4
        assert len(table.selected_dataframe) == 1

    assert 'pandas' not in sys.modules
    print('OK')
    """)


def test_perspective_without_pandas():
    pytest.importorskip('pyarrow')
    _run_without_pandas("""\
    import pyarrow as pa
    import panel as pn

    from bokeh.document import Document

    psp = pn.pane.Perspective(pa.table({'a': [1, 2]}))
    psp.get_root(Document())
    psp.stream({'a': [3]})
    psp.patch({'a': [(0, 10)]})
    assert psp.object['a'].to_pylist() == [10, 2, 3]

    assert 'pandas' not in sys.modules
    print('OK')
    """)


def test_chat_message_csv_without_pandas():
    pytest.importorskip('polars')
    _run_without_pandas("""\
    import polars as pl
    import panel as pn

    from panel.chat.message import _FileInputMessage

    message = pn.chat.ChatMessage(_FileInputMessage(b'a,b\\n1,2\\n', 'data.csv', 'text/csv'))
    df = message._object_panel.object
    assert isinstance(df, pl.DataFrame), type(df)

    assert 'pandas' not in sys.modules
    print('OK')
    """)


def test_admin_without_pandas_errors():
    _run_without_pandas("""\
    try:
        import panel.io.admin
    except ImportError as e:
        assert 'requires pandas' in str(e)
        print('OK')
    """)
