"""
Playwright test for the ipyscore anywidget example.

Tests:
    1. Widget renders (Bokeh root attached to DOM)
    2. Component has expected params (_notes, _draw, _clef)
    3. Python -> browser sync (build and draw a new score)
"""
import pytest

pytest.importorskip("ipyscore")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component

from .conftest import assert_no_console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui


def _make_pane():
    from ipyscore import Widget as ScoreWidget
    widget = ScoreWidget(width=500, height=200)
    score = widget.new_score()
    notes = score.notes("C4/q, D4/q, E4/q, F4/q")
    voice = score.voice(notes)
    system = widget.new_system()
    stave = system.add_stave(voices=[voice])
    stave.add_clef("treble").add_time_signature("4/4")
    widget.draw()
    return pn.pane.AnyWidget(widget, height=250), widget


def test_ipyscore_renders(page):
    """ipyscore widget renders music notation."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=15_000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=10_000)

    assert_no_console_errors(msgs)


def test_ipyscore_component_has_expected_params(page):
    """The wrapped component exposes _notes, _draw, _clef params."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)

    component = pane.component
    assert hasattr(component, '_notes')
    assert hasattr(component, '_draw')
    assert hasattr(component, '_clef')
    assert hasattr(component, '_time_signature')

    assert_no_console_errors(msgs)


def test_ipyscore_python_rebuilds_score(page):
    """Building a new score from Python triggers a re-render."""
    from ipyscore import Widget as ScoreWidget
    widget = ScoreWidget(width=500, height=200)
    score = widget.new_score()
    notes = score.notes("C4/q, D4/q, E4/q, F4/q")
    voice = score.voice(notes)
    system = widget.new_system()
    stave = system.add_stave(voices=[voice])
    stave.add_clef("treble").add_time_signature("4/4")
    widget.draw()

    pane = pn.pane.AnyWidget(widget, height=250)
    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=15_000)
    page.wait_for_timeout(2000)

    # Rebuild with different notes
    score2 = widget.new_score()
    notes2 = score2.notes("G4/q, A4/q, B4/q, C5/q")
    voice2 = score2.voice(notes2)
    system2 = widget.new_system()
    stave2 = system2.add_stave(voices=[voice2])
    stave2.add_clef("bass").add_time_signature("3/4")
    widget.draw()

    page.wait_for_timeout(2000)

    assert_no_console_errors(msgs)
