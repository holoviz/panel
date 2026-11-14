import numpy as np
import pytest

from panel.pane import Vizzu

pl = pytest.importorskip('polars')
pa = pytest.importorskip('pyarrow')

DATA = {'x': ['a', 'b'], 'y': [1.0, 2.0]}


@pytest.fixture(params=[pl.DataFrame, pa.table], ids=['polars', 'pyarrow'])
def frame(request):
    return request.param(DATA)


def test_vizzu_applies_indexless(frame):
    assert Vizzu.applies(frame) == 0


def test_vizzu_indexless_data(frame, document, comm):
    vizzu = Vizzu(frame)
    model = vizzu.get_root(document, comm)

    assert list(model.source.data) == ['x', 'y']
    np.testing.assert_array_equal(model.source.data['y'], [1.0, 2.0])
    assert model.columns == [
        {'name': 'x', 'type': 'dimension'}, {'name': 'y', 'type': 'measure'}
    ]


def test_vizzu_indexless_stream_and_patch(frame, document, comm):
    vizzu = Vizzu(frame)
    model = vizzu.get_root(document, comm)

    vizzu.stream({'x': ['c'], 'y': [3.0]})
    vizzu.patch({'y': [(0, 10.0)]})

    assert type(vizzu.object) is type(frame)
    np.testing.assert_array_equal(model.source.data['y'], [10.0, 2.0, 3.0])
    np.testing.assert_array_equal(model.source.data['x'], ['a', 'b', 'c'])
