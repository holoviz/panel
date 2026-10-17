import pytest

pytest.importorskip("playwright")
hv = pytest.importorskip("holoviews")

from panel.depends import bind
from panel.pane import HoloViews
from panel.tests.util import serve_component, wait_until
from panel.widgets import IntSlider

pytestmark = pytest.mark.ui

GET_PROPERTY = """
([id, prop]) => {
  const model = Bokeh.documents[0].get_model_by_id(id)
  return model == null ? null : model[prop]
}
"""


def test_holoviews_ref_update_patches_rendered_plot(page):
    """A compatible update from a reference patches the plot in the browser instead of replacing it."""
    slider = IntSlider(value=1, start=0, end=100)
    pane = HoloViews(bind(lambda n: hv.Curve([0, n]), slider), backend='bokeh')

    serve_component(page, pane)

    wait_until(lambda: len(pane._models) == 1, page)
    fig = next(iter(pane._models.values()))[0]
    y_range = fig.y_range
    assert page.evaluate(GET_PROPERTY, [y_range.id, 'end']) < 2

    slider.value = 100

    wait_until(lambda: (page.evaluate(GET_PROPERTY, [y_range.id, 'end']) or 0) > 100, page)
    assert next(iter(pane._models.values()))[0] is fig
    assert page.evaluate(GET_PROPERTY, [fig.id, 'id']) == fig.id
