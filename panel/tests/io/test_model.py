import pytest

from bokeh.models import ColumnDataSource

from panel.io.model import _add_geometry_serializers, patch_cds_msg


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


def test_geometry_serializer_encodes_wkt():
    """Shapely geometry serializes as WKT text instead of crashing Bokeh."""
    pytest.importorskip("shapely")
    import numpy as np

    from bokeh.core.serialization import Serializer
    from shapely.geometry import MultiPolygon, Point, Polygon

    _add_geometry_serializers()

    cds = ColumnDataSource(data={"geometry": np.array(
        [MultiPolygon([Polygon([(0, 0), (1, 0), (1, 1)])]), Point(2, 2)],
        dtype=object,
    )})
    encoded = Serializer().encode(cds.data)
    values = encoded["entries"][0][1]["array"]
    assert values[0].startswith("MULTIPOLYGON")
    assert values[1] == "POINT (2 2)"
