import pytest

anywidget = pytest.importorskip("anywidget")
import traitlets

import panel as pn

from panel.pane import AnyWidget, PaneBase
from panel.pane.anywidget import _COMPONENT_CACHE, _find_original_class

# ---------------------------------------------------------------
# Test widget classes (real anywidget subclasses)
# ---------------------------------------------------------------

class CounterWidget(anywidget.AnyWidget):
    _esm = """
    function render({ model, el }) {
        let btn = document.createElement("button");
        btn.innerHTML = `count is ${model.get("value")}`;
        btn.addEventListener("click", () => {
            model.set("value", model.get("value") + 1);
            model.save_changes();
        });
        model.on("change:value", () => {
            btn.innerHTML = `count is ${model.get("value")}`;
        });
        el.appendChild(btn);
    }
    export default { render };
    """
    value = traitlets.Int(0).tag(sync=True)


class StyledWidget(anywidget.AnyWidget):
    _esm = """
    function render({ model, el }) {
        el.innerHTML = `<span class="styled">${model.get("title")}</span>`;
    }
    export default { render };
    """
    _css = ".styled { color: red; }"
    title = traitlets.Unicode("hello").tag(sync=True)


class MultiTraitWidget(anywidget.AnyWidget):
    _esm = """
    function render({ model, el }) { el.innerHTML = "multi"; }
    export default { render };
    """
    count = traitlets.Int(0).tag(sync=True)
    label = traitlets.Unicode("").tag(sync=True)
    flag = traitlets.Bool(False).tag(sync=True)
    data = traitlets.List([]).tag(sync=True)
    config = traitlets.Dict({}).tag(sync=True)


class NameCollisionWidget(anywidget.AnyWidget):
    _esm = """
    function render({ model, el }) { el.innerHTML = "collision"; }
    export default { render };
    """
    name = traitlets.Unicode("collides").tag(sync=True)
    width = traitlets.Int(100).tag(sync=True)


# ---------------------------------------------------------------
# Detection / applies
# ---------------------------------------------------------------

def test_anywidget_applies_true():
    widget = CounterWidget()
    result = AnyWidget.applies(widget)
    assert result

def test_anywidget_applies_false():
    assert AnyWidget.applies("a string") is False
    assert AnyWidget.applies(42) is False
    assert AnyWidget.applies({"key": "val"}) is False
    assert AnyWidget.applies([1, 2, 3]) is False

    # A plain HasTraits object (no _esm) should also be False
    class PlainTraits(traitlets.HasTraits):
        x = traitlets.Int(0)

    assert AnyWidget.applies(PlainTraits()) is False

def test_anywidget_auto_detection():
    widget = CounterWidget()
    assert PaneBase.get_pane_type(widget) is AnyWidget

def test_anywidget_pn_panel():
    widget = CounterWidget()
    pane = pn.panel(widget)
    assert isinstance(pane, AnyWidget)

def test_anywidget_priority_over_ipywidget():
    try:
        from panel.pane import IPyWidget
    except Exception:
        pytest.skip("IPyWidget not available")
    assert AnyWidget.priority > IPyWidget.priority


# ---------------------------------------------------------------
# Model creation
# ---------------------------------------------------------------

def test_anywidget_get_root(document, comm):
    widget = CounterWidget()
    pane = AnyWidget(widget)
    model = pane.get_root(document, comm=comm)
    assert model is not None

def test_anywidget_component_created(document, comm):
    widget = CounterWidget()
    pane = AnyWidget(widget)
    pane.get_root(document, comm=comm)
    assert pane.component is not None

def test_anywidget_component_eager_creation():
    """Component is available immediately after construction, before render."""
    widget = CounterWidget(value=42)
    pane = AnyWidget(widget)
    # No get_root() call — component should exist eagerly
    assert pane.component is not None
    assert pane.component.value == 42


# ---------------------------------------------------------------
# Initial values
# ---------------------------------------------------------------

def test_anywidget_component_initial_values(document, comm):
    widget = CounterWidget(value=42)
    pane = AnyWidget(widget)
    pane.get_root(document, comm=comm)
    assert pane.component.value == 42


# ---------------------------------------------------------------
# Bidirectional sync
# ---------------------------------------------------------------

def test_anywidget_sync_before_render():
    """Bidirectional sync works before any render call, using eager component."""
    widget = CounterWidget(value=0)
    pane = AnyWidget(widget)

    # param.watch on the component (no get_root needed)
    observed = []
    pane.component.param.watch(lambda e: observed.append(e.new), ['value'])

    widget.value = 5
    assert pane.component.value == 5
    assert observed == [5]

    # Reverse direction
    pane.component.value = 10
    assert widget.value == 10

def test_anywidget_sync_traitlet_to_component(document, comm):
    widget = CounterWidget()
    pane = AnyWidget(widget)
    pane.get_root(document, comm=comm)

    widget.value = 7
    assert pane.component.value == 7

def test_anywidget_sync_component_to_traitlet(document, comm):
    widget = CounterWidget()
    pane = AnyWidget(widget)
    pane.get_root(document, comm=comm)

    pane.component.value = 99
    assert widget.value == 99

def test_anywidget_sync_component_to_traitlet_observe(document, comm):
    """Verify that traitlet observe callbacks fire when the component
    changes a value (simulates the browser-click -> slider update pattern
    from the POC demo)."""
    widget = CounterWidget()
    pane = AnyWidget(widget)
    pane.get_root(document, comm=comm)

    observed = []
    widget.observe(lambda change: observed.append(change['new']), names=['value'])

    pane.component.value = 10
    assert widget.value == 10
    assert observed == [10]

    pane.component.value = 20
    assert observed == [10, 20]

def test_anywidget_sync_no_loop(document, comm):
    widget = CounterWidget()
    pane = AnyWidget(widget)
    pane.get_root(document, comm=comm)

    # Rapidly toggle values — should not raise or infinite loop
    for i in range(20):
        widget.value = i
    assert pane.component.value == 19
    assert widget.value == 19

def test_anywidget_multi_trait_sync(document, comm):
    widget = MultiTraitWidget(count=5, label="hi", flag=True, data=[1, 2], config={"a": 1})
    pane = AnyWidget(widget)
    pane.get_root(document, comm=comm)

    # Check initial values propagated
    assert pane.component.count == 5
    assert pane.component.label == "hi"
    assert pane.component.flag is True
    assert pane.component.data == [1, 2]
    assert pane.component.config == {"a": 1}

    # traitlet -> component
    widget.count = 10
    assert pane.component.count == 10

    widget.label = "bye"
    assert pane.component.label == "bye"

    widget.flag = False
    assert pane.component.flag is False

    widget.data = [3, 4, 5]
    assert pane.component.data == [3, 4, 5]

    widget.config = {"b": 2}
    assert pane.component.config == {"b": 2}

    # component -> traitlet
    pane.component.count = 20
    assert widget.count == 20

    pane.component.label = "again"
    assert widget.label == "again"


# ---------------------------------------------------------------
# CSS extraction
# ---------------------------------------------------------------

def test_anywidget_css_extraction(document, comm):
    widget = StyledWidget()
    pane = AnyWidget(widget)
    pane.get_root(document, comm=comm)

    component_cls = type(pane.component)
    assert hasattr(component_cls, '_stylesheets')
    assert any(".styled" in s for s in component_cls._stylesheets)


# ---------------------------------------------------------------
# Name collision handling
# ---------------------------------------------------------------

def test_anywidget_name_collision(document, comm):
    widget = NameCollisionWidget()
    pane = AnyWidget(widget)
    pane.get_root(document, comm=comm)

    component = pane.component
    # `name` and `width` collide with AnyWidgetComponent params,
    # so they should get `w_` prefix
    assert hasattr(component, 'w_name')
    assert hasattr(component, 'w_width')
    assert component.w_name == "collides"
    assert component.w_width == 100

    # Sync should still work through the prefixed params
    widget.name = "updated"
    assert component.w_name == "updated"


# ---------------------------------------------------------------
# Cache reuse
# ---------------------------------------------------------------

def test_anywidget_cache_reuse():
    # Clear cache to isolate this test
    _COMPONENT_CACHE.clear()

    w1 = CounterWidget()
    w2 = CounterWidget()

    orig1 = _find_original_class(w1)
    orig2 = _find_original_class(w2)
    assert orig1 is orig2

    from panel.pane.anywidget import _get_or_create_component_class
    cls1 = _get_or_create_component_class(w1)
    cls2 = _get_or_create_component_class(w2)
    assert cls1 is cls2


# ---------------------------------------------------------------
# Object replacement
# ---------------------------------------------------------------

def test_anywidget_object_replacement(document, comm):
    w1 = CounterWidget(value=1)
    w2 = CounterWidget(value=2)

    pane = AnyWidget(w1)
    pane.get_root(document, comm=comm)

    old_component = pane.component
    assert old_component is not None
    assert old_component.value == 1

    # Replace the object
    pane.object = w2
    new_component = pane.component

    # New component should be created
    assert new_component is not old_component
    assert new_component.value == 2

    # Old widget changes should NOT affect new component
    w1.value = 999
    assert new_component.value == 2

    # New widget sync should work
    w2.value = 42
    assert new_component.value == 42


# ---------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------

def test_anywidget_cleanup(document, comm):
    widget = CounterWidget()
    pane = AnyWidget(widget)
    model = pane.get_root(document, comm=comm)

    assert pane.component is not None
    assert pane._models != {}

    pane._cleanup(model)

    assert pane._models == {}
    assert pane._component is None
    assert pane._trait_watchers == []
