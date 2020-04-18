from bokeh.models import ColumnDataSource

from panel.io.model import patch_cds_msg

def test_patch_cds_typed_array():
    cds = ColumnDataSource()
    msg = {
        'header': {'msgid': 'TEST', 'msgtype': 'PATCH-DOC'},
        'metadata': {},
        'content': {
            'events': [{
                'kind': 'ModelChanged',
                'model': {'id': cds.ref['id']},
                'attr': 'data',
                'new': {
                    'a': {'2': 2, '0': 0, '1': 1},
                    'b': {'0': 'a', '2': 'c', '1': 'b'}
                }
            }],
            'references': []
        },
        'buffers': []
    }
    expected = {
        'header': {'msgid': 'TEST', 'msgtype': 'PATCH-DOC'},
        'metadata': {},
        'content': {
            'events': [{
                'kind': 'ModelChanged',
                'model': {'id': cds.ref['id']},
                'attr': 'data',
                'new': {
                    'a': [0, 1, 2],
                    'b': ['a', 'b', 'c']
                }
            }],
            'references': []
        },
        'buffers': []
    }
    patch_cds_msg(cds, msg)
    assert msg == expected
