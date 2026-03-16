import pytest

from panel.widgets.indicators import (
    Dial, Gauge, Number, Tqdm,
)


def test_number_none(document, comm):
    number = Number(value=None, name='Value')

    model = number.get_root(document, comm)

    assert model.text.endswith("&lt;div style=&quot;font-size: 54pt; color: currentcolor&quot;&gt;-&lt;/div&gt;")

    number.nan_format = 'nan'

    assert model.text.endswith("&lt;div style=&quot;font-size: 54pt; color: currentcolor&quot;&gt;nan&lt;/div&gt;")


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


def test_gauge_creation():
    gauge = Gauge(name="Test", value=50, bounds=(0, 100))
    assert gauge.value == 50
    assert gauge.bounds == (0, 100)
    assert gauge.name == "Test"


def test_gauge_colors():
    gauge = Gauge(value=75, colors=[(0.4, 'green'), (0.8, 'yellow'), (1, 'red')])
    assert gauge.colors == [(0.4, 'green'), (0.8, 'yellow'), (1, 'red')]


def test_gauge_custom_opts():
    gauge = Gauge(value=50, custom_opts={'pointer': {'width': 5}})
    assert gauge.custom_opts == {'pointer': {'width': 5}}


def test_gauge_process_param_change():
    gauge = Gauge(name="G", value=50, bounds=(0, 100))
    msg = gauge._process_param_change({
        'value': 50, 'bounds': (0, 100), 'tooltip_format': '{b} : {c}%',
        'show_ticks': True, 'show_labels': True, 'title_size': 18,
        'format': '{value}%', 'start_angle': 225, 'end_angle': -45,
        'num_splits': 10, 'annulus_width': 10,
    })
    assert 'data' in msg
    assert msg['data']['series'][0]['type'] == 'gauge'
    assert msg['data']['series'][0]['data'][0]['value'] == 50
    assert msg['data']['series'][0]['min'] == 0
    assert msg['data']['series'][0]['max'] == 100


def test_gauge_process_param_change_with_colors():
    gauge = Gauge(name="G", value=75, bounds=(0, 100),
                  colors=[(0.5, 'green'), (1, 'red')])
    msg = gauge._process_param_change({
        'value': 75, 'bounds': (0, 100), 'tooltip_format': '{b} : {c}%',
        'show_ticks': True, 'show_labels': True, 'title_size': 18,
        'format': '{value}%', 'start_angle': 225, 'end_angle': -45,
        'num_splits': 10, 'annulus_width': 10,
        'colors': [(0.5, 'green'), (1, 'red')],
    })
    assert msg['data']['series'][0]['axisLine']['lineStyle']['color'] == [
        (0.5, 'green'), (1, 'red')
    ]


def test_tqdm_color():
    tqdm = Tqdm()
    tqdm.text_pane.styles={'color': 'green'}
    for _ in tqdm(range(2)):
        pass
    assert tqdm.text_pane.styles["color"]=="green"
