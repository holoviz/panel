import pytest

from panel.widgets.indicators import (
    Dial, Gauge, Number, Tqdm,
)


def test_number_none(document, comm):
    number = Number(value=None, name='Value')

    model = number.get_root(document, comm)

    assert model.text.endswith("&lt;div style=&quot;font-size: 54pt; color: black&quot;&gt;-&lt;/div&gt;")

    number.nan_format = 'nan'

    assert model.text.endswith("&lt;div style=&quot;font-size: 54pt; color: black&quot;&gt;nan&lt;/div&gt;")


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


def test_dial_none(document, comm):
    dial = Dial(value=None, name='Value')

    model = dial.get_root(document, comm)

    cds = model.select(name='annulus_source')

    assert list(cds.data['starts']) == [9.861110273767961, 9.861110273767961]
    assert list(cds.data['ends']) == [9.861110273767961, 5.846852994181004]

    text_cds = model.select(name='label_source')

    assert text_cds.data['text'] == ['Value', '-%', '0%', '100%']

    dial.nan_format = 'nan'

    assert text_cds.data['text'] == ['Value', 'nan%', '0%', '100%']


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

def test_tqdm_color():
    tqdm = Tqdm()
    tqdm.text_pane.styles={'color': 'green'}
    for _ in tqdm(range(0,2)):
        pass
    assert tqdm.text_pane.styles["color"]=="green"
