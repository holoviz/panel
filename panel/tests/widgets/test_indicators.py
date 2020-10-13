import pytest

from panel.widgets.indicators import Dial, Gauge, Number


def test_number_thresholds(document, comm):
    number = Number(value=0, colors=[(0.33, 'green'), (0.66, 'yellow'), (1, 'red')])

    model = number.get_root(document, comm)

    assert 'green' in model.text

    number.value = 0.5

    assert 'yellow' in model.text

    number.value = 0.7

    assert 'red' in model.text


def test_dial_thresholds(document, comm):
    dial = Dial(value=0, colors=[(0.33, 'green'), (0.66, 'yellow'), (1, 'red')])

    model = dial.get_root(document, comm)

    cds = model.select(name='annulus_source')

    assert ['green', 'whitesmoke'] == cds.data['color']

    dial.value = 50

    assert ['yellow', 'whitesmoke'] == cds.data['color']

    dial.value = 72

    assert ['red', 'whitesmoke'] == cds.data['color']

    
def test_dial_thresholds_with_bounds(document, comm):
    dial = Dial(value=25, colors=[(0.33, 'green'), (0.66, 'yellow'), (1, 'red')],
                bounds=(25, 75))

    model = dial.get_root(document, comm)

    cds = model.select(name='annulus_source')

    assert ['green', 'whitesmoke'] == cds.data['color']

    dial.value = 50

    assert ['yellow', 'whitesmoke'] == cds.data['color']

    dial.value = 75

    assert ['red', 'whitesmoke'] == cds.data['color']


def test_dial_bounds():
    dial = Dial(bounds=(0, 20))

    with pytest.raises(ValueError):
        dial.value = 100


def test_gauge_bounds():
    dial = Gauge(bounds=(0, 20))

    with pytest.raises(ValueError):
        dial.value = 100
