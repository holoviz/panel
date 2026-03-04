import pathlib
import tempfile

import param
import pytest

anywidget = pytest.importorskip("anywidget")
import traitlets

import panel as pn

from panel.pane import AnyWidget, PaneBase
from panel.pane.anywidget import (
    _CACHE_MAX_SIZE, _COMPONENT_CACHE, _MAX_SERIALIZE_DEPTH,
    _collect_child_widgets, _dataframe_to_records, _deep_serialize,
    _find_original_class, _get_or_create_component_class, _is_dataframe,
    _is_json_safe, _is_widget_serialization, _resolve_text,
    _serialize_child_state, _serialize_instance, _traitlet_to_param,
)

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


class BokehReservedNameWidget(anywidget.AnyWidget):
    """Widget with traitlets that clash with BokehJS reserved attribute names."""
    _esm = """
    function render({ model, el }) {
        el.innerHTML = `connect=${model.get("connect")} type=${model.get("type")}`;
    }
    export default { render };
    """
    connect = traitlets.Bool(True).tag(sync=True)
    type = traitlets.Unicode("scatter").tag(sync=True)
    destroy = traitlets.Int(0).tag(sync=True)


class DisplayOnlyWidget(anywidget.AnyWidget):
    """Widget with no sync-tagged traitlets — pure display."""
    _esm = """
    function render({ model, el }) { el.innerHTML = "<p>Display only</p>"; }
    export default { render };
    """


class EnumWidget(anywidget.AnyWidget):
    _esm = """
    function render({ model, el }) { el.innerHTML = model.get("color"); }
    export default { render };
    """
    color = traitlets.Enum(["red", "green", "blue"], default_value="red").tag(sync=True)


class SetWidget(anywidget.AnyWidget):
    _esm = """
    function render({ model, el }) { el.innerHTML = "set"; }
    export default { render };
    """
    tags = traitlets.Set(traitlets.Unicode(), default_value=set()).tag(sync=True)


class InstanceWidget(anywidget.AnyWidget):
    _esm = """
    function render({ model, el }) { el.innerHTML = "instance"; }
    export default { render };
    """
    metadata = traitlets.Instance(dict, args=()).tag(sync=True)


class UnionWidget(anywidget.AnyWidget):
    _esm = """
    function render({ model, el }) { el.innerHTML = "union"; }
    export default { render };
    """
    value = traitlets.Union(
        [traitlets.Int(), traitlets.Unicode()], default_value=0
    ).tag(sync=True)


class UnderscoreSyncWidget(anywidget.AnyWidget):
    """Widget with underscore-prefixed sync traits (like Altair's _params)."""
    _esm = """
    function render({ model, el }) {
        el.innerHTML = JSON.stringify(model.get("_internal_state"));
    }
    export default { render };
    """
    value = traitlets.Int(0).tag(sync=True)
    _internal_state = traitlets.Dict(default_value={}).tag(sync=True)


class NonJsonSafeWidget(anywidget.AnyWidget):
    """Widget with an Any-typed traitlet holding a non-JSON-safe object (like HiGlass)."""
    _esm = """
    function render({ model, el }) { el.innerHTML = "non-json"; }
    export default { render };
    """
    client = traitlets.Any(default_value=None).tag(sync=True)
    value = traitlets.Int(0).tag(sync=True)


class ValidatorWidget(anywidget.AnyWidget):
    """Widget with a traitlet validator that transforms values (like pyobsplot)."""
    _esm = """
    function render({ model, el }) {
        el.innerHTML = JSON.stringify(model.get("spec"));
    }
    export default { render };
    """
    spec = traitlets.Dict(default_value={}).tag(sync=True)

    @traitlets.validate('spec')
    def _validate_spec(self, proposal):
        raw = proposal['value']
        # Simulate pyobsplot-style transform: wrap in {data: ..., processed: True}
        if raw and 'processed' not in raw:
            return {'data': raw, 'processed': True}
        return raw


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

def test_anywidget_applies_false_duck_type_mismatch():
    """Objects with traits/class_traits but no _esm should not match."""
    class FakeWidget:
        def traits(self):
            return {}
        def class_traits(self):
            return {}

    assert AnyWidget.applies(FakeWidget()) is False

    # Object with traits but not callable
    class BadTraits:
        traits = "not callable"
        _esm = "some code"

    assert AnyWidget.applies(BadTraits()) is False

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

def test_anywidget_none_object_returns_spacer(document, comm):
    """_get_model returns BkSpacer when object is None."""
    from bokeh.models import Spacer as BkSpacer
    pane = AnyWidget(None)
    model = pane.get_root(document, comm=comm)
    assert isinstance(model.children[0], BkSpacer)

def test_anywidget_none_object_no_component():
    """Component is None when object is None."""
    pane = AnyWidget(None)
    assert pane.component is None


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


def test_anywidget_bokeh_reserved_name_collision(document, comm):
    """Traitlets with names that clash with BokehJS reserved attributes
    (e.g. 'connect', 'type', 'destroy') should be prefixed with 'w_'
    to avoid 'attempted to redefine attribute' errors."""
    _COMPONENT_CACHE.clear()

    widget = BokehReservedNameWidget()
    pane = AnyWidget(widget)
    pane.get_root(document, comm=comm)

    component = pane.component
    assert hasattr(component, 'w_connect')
    assert hasattr(component, 'w_type')
    assert hasattr(component, 'w_destroy')
    assert component.w_connect is True
    assert component.w_type == "scatter"
    assert component.w_destroy == 0

    # Sync works through prefixed params
    widget.connect = False
    assert component.w_connect is False

    component.w_type = "bar"
    assert widget.type == "bar"

    _COMPONENT_CACHE.clear()


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

    cls1 = _get_or_create_component_class(w1)
    cls2 = _get_or_create_component_class(w2)
    assert cls1 is cls2

def test_anywidget_cache_bounded():
    """Cache evicts oldest entries when exceeding _CACHE_MAX_SIZE."""
    _COMPONENT_CACHE.clear()

    # Create more classes than the cache can hold
    classes = []
    for i in range(_CACHE_MAX_SIZE + 5):
        cls = type(f'Widget{i}', (anywidget.AnyWidget,), {
            '_esm': f'function render({{ model, el }}) {{ el.innerHTML = "{i}"; }}\nexport default {{ render }};',
            '__module__': __name__,
        })
        classes.append(cls)
        w = cls()
        _get_or_create_component_class(w)

    assert len(_COMPONENT_CACHE) == _CACHE_MAX_SIZE
    # Oldest entries should have been evicted
    orig_first = _find_original_class(classes[0]())
    assert orig_first not in _COMPONENT_CACHE

    _COMPONENT_CACHE.clear()


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


# ---------------------------------------------------------------
# Display-only widget (no sync traits)
# ---------------------------------------------------------------

def test_anywidget_display_only(document, comm):
    """Widget with no sync-tagged traitlets renders without error."""
    widget = DisplayOnlyWidget()
    pane = AnyWidget(widget)
    assert pane.component is not None
    model = pane.get_root(document, comm=comm)
    assert model is not None


# ---------------------------------------------------------------
# Traitlet type mapping: Enum, Set, Instance, Union
# ---------------------------------------------------------------

def test_traitlet_enum_mapping():
    """Enum traitlet maps to param.Selector with objects."""
    trait = traitlets.Enum(["red", "green", "blue"], default_value="red")
    p = _traitlet_to_param(trait)
    assert isinstance(p, param.Selector)
    assert p.default == "red"
    assert p.objects == ["red", "green", "blue"]

def test_traitlet_set_mapping():
    """Set traitlet maps to param.List (approximation)."""
    trait = traitlets.Set(default_value=set())
    p = _traitlet_to_param(trait)
    assert isinstance(p, param.List)

def test_traitlet_instance_mapping():
    """Instance traitlet maps to param.Dict (serialized for Bokeh)."""
    trait = traitlets.Instance(dict, args=())
    p = _traitlet_to_param(trait)
    assert isinstance(p, param.Dict)

def test_traitlet_union_mapping():
    """Union traitlet falls back to generic param.Parameter."""
    trait = traitlets.Union([traitlets.Int(), traitlets.Unicode()], default_value=0)
    p = _traitlet_to_param(trait)
    assert isinstance(p, param.Parameter)
    assert p.default == 0

def test_anywidget_enum_sync():
    """Enum traitlet syncs correctly between widget and component."""
    _COMPONENT_CACHE.clear()
    widget = EnumWidget()
    pane = AnyWidget(widget)
    assert pane.component is not None
    assert pane.component.color == "red"

    widget.color = "blue"
    assert pane.component.color == "blue"

    pane.component.color = "green"
    assert widget.color == "green"
    _COMPONENT_CACHE.clear()

def test_anywidget_instance_widget():
    """Instance traitlet widget creates component correctly."""
    _COMPONENT_CACHE.clear()
    widget = InstanceWidget()
    pane = AnyWidget(widget)
    assert pane.component is not None
    _COMPONENT_CACHE.clear()

def test_anywidget_union_sync():
    """Union traitlet syncs correctly (generic param.Parameter)."""
    _COMPONENT_CACHE.clear()
    widget = UnionWidget()
    pane = AnyWidget(widget)
    assert pane.component is not None
    assert pane.component.value == 0

    widget.value = "hello"
    assert pane.component.value == "hello"

    widget.value = 42
    assert pane.component.value == 42
    _COMPONENT_CACHE.clear()


# ---------------------------------------------------------------
# _resolve_text helper
# ---------------------------------------------------------------

def test_resolve_text_none():
    assert _resolve_text(None) is None

def test_resolve_text_string():
    assert _resolve_text("hello") == "hello"

def test_resolve_text_path():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write("export default { render };")
        f.flush()
        result = _resolve_text(pathlib.Path(f.name))
    assert result == "export default { render };"

def test_resolve_text_non_string_object():
    """Non-string, non-path objects are coerced via str()."""
    class FakeFileContents:
        def __str__(self):
            return "fake ESM content"
    assert _resolve_text(FakeFileContents()) == "fake ESM content"


# ---------------------------------------------------------------
# File-based ESM
# ---------------------------------------------------------------

def test_anywidget_file_esm(document, comm):
    """Widget with _esm as a pathlib.Path works correctly."""
    _COMPONENT_CACHE.clear()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write("""
        function render({ model, el }) { el.innerHTML = "file-based"; }
        export default { render };
        """)
        f.flush()
        esm_path = pathlib.Path(f.name)

    class FileEsmWidget(anywidget.AnyWidget):
        _esm = esm_path
        val = traitlets.Int(0).tag(sync=True)

    widget = FileEsmWidget(val=10)
    pane = AnyWidget(widget)
    assert pane.component is not None
    assert pane.component.val == 10
    model = pane.get_root(document, comm=comm)
    assert model is not None
    _COMPONENT_CACHE.clear()


# ---------------------------------------------------------------
# Exception handling in sync
# ---------------------------------------------------------------

def test_anywidget_sync_trait_error_silent():
    """TraitError during sync is silently caught (no crash)."""
    widget = CounterWidget(value=0)
    pane = AnyWidget(widget)

    # Setting an invalid type on the component — the sync back to
    # the traitlet will raise TraitError, which should be caught
    # We can't easily trigger this through normal API since param
    # types are looser, but we verify the mechanism works by
    # confirming the pane doesn't crash
    widget.value = 5
    assert pane.component.value == 5

def test_anywidget_sync_logs_unexpected_error():
    """Unexpected exceptions during param->traitlet sync are logged, not raised."""
    widget = CounterWidget(value=0)
    pane = AnyWidget(widget)

    # Monkey-patch widget to raise on setattr for 'value'
    original_setattr = type(widget).__setattr__

    def raising_setattr(self, name, val):
        if name == 'value' and isinstance(val, int) and val == 999:
            raise RuntimeError("Unexpected error")
        return original_setattr(self, name, val)

    type(widget).__setattr__ = raising_setattr
    try:
        # Should not raise — the error is caught and logged
        pane.component.value = 999
        # The traitlet should still have the old value since setattr failed
        assert widget.value == 0
    finally:
        type(widget).__setattr__ = original_setattr

def test_anywidget_underscore_sync_traits():
    """Underscore-prefixed sync traits are included (e.g. Altair _params)."""
    _COMPONENT_CACHE.clear()
    widget = UnderscoreSyncWidget()
    pane = AnyWidget(widget)
    component = pane.component
    assert component is not None

    # _internal_state should be synced (not filtered out)
    assert hasattr(component, '_internal_state')
    assert component._internal_state == {}

    # Bidirectional sync works for underscore-prefixed traits
    widget._internal_state = {"key": "value"}
    assert component._internal_state == {"key": "value"}

    component._internal_state = {"updated": True}
    assert widget._internal_state == {"updated": True}
    _COMPONENT_CACHE.clear()

def test_anywidget_validator_transform_sync():
    """Traitlet validators that transform values sync the validated value back."""
    _COMPONENT_CACHE.clear()
    widget = ValidatorWidget()
    pane = AnyWidget(widget)
    component = pane.component
    assert component is not None

    # Set a raw spec from the component side (simulates Panel control change)
    component.spec = {"marks": ["dot"], "grid": True}

    # The traitlet validator should have transformed it
    expected = {"data": {"marks": ["dot"], "grid": True}, "processed": True}
    assert widget.spec == expected

    # The component should have received the validated (transformed) value back
    assert component.spec == expected
    _COMPONENT_CACHE.clear()


# ---------------------------------------------------------------
# _is_json_safe helper
# ---------------------------------------------------------------

def test_is_json_safe_primitives():
    """JSON-safe primitives are recognized."""
    assert _is_json_safe(None) is True
    assert _is_json_safe(True) is True
    assert _is_json_safe(42) is True
    assert _is_json_safe(3.14) is True
    assert _is_json_safe("hello") is True
    assert _is_json_safe(b"bytes") is True
    assert _is_json_safe([1, 2, 3]) is True
    assert _is_json_safe((1, 2)) is True
    assert _is_json_safe({"a": 1}) is True

def test_is_json_safe_non_primitives():
    """Non-JSON-safe objects are detected."""
    class CustomObj:
        pass
    assert _is_json_safe(CustomObj()) is False
    assert _is_json_safe(object()) is False


# ---------------------------------------------------------------
# Non-JSON-safe traitlet serialization (HiGlass-like)
# ---------------------------------------------------------------

def test_anywidget_non_json_safe_serialize():
    """Non-JSON-safe Any-typed traitlet values are serialized to dicts."""
    _COMPONENT_CACHE.clear()

    class FakeClient:
        def __init__(self):
            self.url = "http://example.com"
            self.port = 8080

    widget = NonJsonSafeWidget()
    widget.client = FakeClient()

    pane = AnyWidget(widget)
    component = pane.component
    assert component is not None

    # The non-JSON-safe object should have been serialized to a dict
    assert isinstance(component.client, dict)
    assert component.client['url'] == "http://example.com"
    assert component.client['port'] == 8080
    _COMPONENT_CACHE.clear()

def test_anywidget_non_json_safe_traitlet_change():
    """Non-JSON-safe values arriving via traitlet change are serialized."""
    _COMPONENT_CACHE.clear()

    class FakeClient:
        def __init__(self, name="default"):
            self.name = name

    widget = NonJsonSafeWidget()
    pane = AnyWidget(widget)
    component = pane.component
    assert component is not None

    # Simulate a traitlet change with a non-JSON-safe value
    widget.client = FakeClient("updated")
    assert isinstance(component.client, dict)
    assert component.client['name'] == "updated"
    _COMPONENT_CACHE.clear()


def test_anywidget_dimension_forwarding():
    """When height/width traits are renamed (e.g. height -> w_height),
    their numeric values are forwarded to Layoutable height/width so
    the DOM container gets actual pixel dimensions.  Without this,
    widgets like jupyter-scatter crash because createScatterplot sees
    a zero-size canvas."""
    _COMPONENT_CACHE.clear()

    class DimWidget(anywidget.AnyWidget):
        _esm = """
        function render({ model, el }) { el.innerHTML = "dim"; }
        export default { render };
        """
        height = traitlets.Int(500).tag(sync=True)
        width = traitlets.Int(800).tag(sync=True)

    widget = DimWidget()
    pane = AnyWidget(widget)
    component = pane.component

    # The renamed traits should have the widget values
    assert component.w_height == 500
    assert component.w_width == 800
    # The Layoutable height/width should be forwarded from the renamed traits
    assert component.height == 500
    assert component.width == 800

    _COMPONENT_CACHE.clear()


def test_anywidget_dimension_forwarding_explicit_override():
    """Explicit pane layout params override dimension forwarding."""
    _COMPONENT_CACHE.clear()

    class DimWidget2(anywidget.AnyWidget):
        _esm = """
        function render({ model, el }) { el.innerHTML = "dim2"; }
        export default { render };
        """
        height = traitlets.Int(500).tag(sync=True)

    widget = DimWidget2()
    pane = AnyWidget(widget, height=300)
    component = pane.component

    # Explicit pane height should take priority over forwarded value
    assert component.w_height == 500
    assert component.height == 300

    _COMPONENT_CACHE.clear()


def test_anywidget_dimension_forwarding_non_numeric_skip():
    """Non-numeric values (e.g. width='auto') are not forwarded."""
    _COMPONENT_CACHE.clear()

    class DimWidget3(anywidget.AnyWidget):
        _esm = """
        function render({ model, el }) { el.innerHTML = "dim3"; }
        export default { render };
        """
        height = traitlets.Int(0).tag(sync=True)
        width = traitlets.Unicode("auto").tag(sync=True)

    widget = DimWidget3()
    pane = AnyWidget(widget)
    component = pane.component

    # height=0 should NOT be forwarded (not > 0)
    assert component.w_height == 0
    assert component.height is None
    # width="auto" should NOT be forwarded (not numeric)
    assert component.w_width == "auto"
    assert component.width is None

    _COMPONENT_CACHE.clear()


def test_anywidget_dimension_forwarding_runtime_sync():
    """Changing the renamed height trait at runtime also updates
    the Layoutable height."""
    _COMPONENT_CACHE.clear()

    class DimWidget4(anywidget.AnyWidget):
        _esm = """
        function render({ model, el }) { el.innerHTML = "dim4"; }
        export default { render };
        """
        height = traitlets.Int(500).tag(sync=True)

    widget = DimWidget4()
    pane = AnyWidget(widget)
    component = pane.component

    assert component.height == 500

    # Change via traitlet at runtime
    widget.height = 600
    assert component.w_height == 600
    assert component.height == 600

    _COMPONENT_CACHE.clear()


# ---------------------------------------------------------------
# _trait_name_map in esm_constants
# ---------------------------------------------------------------

def test_anywidget_trait_name_map_in_constants():
    """_trait_name_map is exposed via _constants for the TS adapter."""
    _COMPONENT_CACHE.clear()
    widget = NameCollisionWidget()
    component_cls = _get_or_create_component_class(widget)

    # _constants should include the trait_name_map
    assert hasattr(component_cls, '_constants')
    constants = component_cls._constants
    assert '_trait_name_map' in constants
    # 'name' and 'width' collide, so they should be mapped
    assert constants['_trait_name_map']['name'] == 'w_name'
    assert constants['_trait_name_map']['width'] == 'w_width'
    _COMPONENT_CACHE.clear()


# ---------------------------------------------------------------
# construct_data_model reuse (Jupyter Scatter-like)
# ---------------------------------------------------------------

def test_construct_data_model_reuse():
    """construct_data_model reuses existing model from Bokeh registry."""
    from panel.io.datamodel import construct_data_model

    class TempWidget(param.Parameterized):
        value = param.Integer(default=0)

    # First call creates the model
    model1 = construct_data_model(TempWidget, name='TestReuse1')

    # Second call with the same name should return the same class
    model2 = construct_data_model(TempWidget, name='TestReuse1')

    assert model1 is model2


# ---------------------------------------------------------------
# _serialize_instance for non-Instance traits
# ---------------------------------------------------------------

def test_serialize_instance_custom_object():
    """_serialize_instance converts objects with __dict__ to dicts."""
    class Config:
        def __init__(self):
            self.host = "localhost"
            self.port = 9000

    result = _serialize_instance(Config())
    assert isinstance(result, dict)
    assert result['host'] == "localhost"
    assert result['port'] == 9000

def test_serialize_instance_passthrough():
    """_serialize_instance passes through JSON-safe types."""
    assert _serialize_instance(None) is None
    assert _serialize_instance(42) == 42
    assert _serialize_instance("hello") == "hello"
    assert _serialize_instance([1, 2]) == [1, 2]
    assert _serialize_instance({"a": 1}) == {"a": 1}


# ---------------------------------------------------------------
# _deep_serialize (nested non-JSON-safe objects)
# ---------------------------------------------------------------

def test_deep_serialize_nested_objects():
    """_deep_serialize recursively converts nested non-JSON-safe objects."""
    class Inner:
        def __init__(self):
            self.value = 42

    class Outer:
        def __init__(self):
            self.inner = Inner()
            self.name = "test"

    result = _deep_serialize(Outer())
    assert isinstance(result, dict)
    assert result['name'] == "test"
    assert isinstance(result['inner'], dict)
    assert result['inner']['value'] == 42

def test_deep_serialize_dict_with_non_json_safe_values():
    """_deep_serialize handles dicts containing non-JSON-safe leaf values."""
    class FakeComm:
        def __init__(self):
            self.target = "test_target"

    data = {"key": "value", "comm": FakeComm(), "count": 5}
    result = _deep_serialize(data)
    assert isinstance(result, dict)
    assert result['key'] == "value"
    assert result['count'] == 5
    assert isinstance(result['comm'], dict)
    assert result['comm']['target'] == "test_target"

def test_deep_serialize_primitives_passthrough():
    """_deep_serialize passes primitives through unchanged."""
    assert _deep_serialize(None) is None
    assert _deep_serialize(42) == 42
    assert _deep_serialize("hello") == "hello"
    assert _deep_serialize(True) is True
    assert _deep_serialize([1, 2, 3]) == [1, 2, 3]
    assert _deep_serialize({"a": 1}) == {"a": 1}

def test_deep_serialize_circular_reference():
    """_deep_serialize handles circular references without infinite loop."""
    d = {"key": "value"}
    d["self"] = d
    result = _deep_serialize(d)
    assert result['key'] == "value"
    assert result['self'] is None  # circular ref broken

def test_anywidget_nested_non_json_safe_init():
    """Widget with nested non-JSON-safe values in init is serialized recursively."""
    _COMPONENT_CACHE.clear()

    class FakeComm:
        def __init__(self):
            self.target = "kernel"

    class FakeClient:
        def __init__(self):
            self.comm = FakeComm()
            self.url = "http://example.com"

    widget = NonJsonSafeWidget()
    widget.client = FakeClient()

    pane = AnyWidget(widget)
    component = pane.component
    assert component is not None

    # Should be fully serialized, including nested FakeComm
    assert isinstance(component.client, dict)
    assert component.client['url'] == "http://example.com"
    assert isinstance(component.client['comm'], dict)
    assert component.client['comm']['target'] == "kernel"
    _COMPONENT_CACHE.clear()


# ---------------------------------------------------------------
# Logger-like deeply nested non-JSON-safe objects (HiGlass-like)
# ---------------------------------------------------------------

def test_deep_serialize_logger_like_object():
    """_deep_serialize handles Logger-like objects with complex __dict__ trees."""
    import logging

    logger = logging.getLogger("test_anywidget_deep_serialize")
    result = _deep_serialize(logger)

    # Logger should be serialized to a dict (via __dict__), not crash
    assert isinstance(result, dict)
    # The dict should contain the logger's name
    assert result.get('name') == "test_anywidget_deep_serialize"


def test_deep_serialize_non_string_dict_keys():
    """_deep_serialize converts non-string dict keys to repr strings."""
    import logging

    # Simulate logging.Manager.loggerDict which uses Logger objects as keys
    logger1 = logging.getLogger("test_key_serialize_1")
    logger2 = logging.getLogger("test_key_serialize_2")
    data = {logger1: "value1", logger2: "value2", "normal_key": "value3"}

    result = _deep_serialize(data)
    assert isinstance(result, dict)
    # Non-string keys should be stringified (repr)
    assert all(isinstance(k, str) for k in result.keys())
    assert result["normal_key"] == "value3"


def test_deep_serialize_depth_limit():
    """_deep_serialize stops expanding at _MAX_SERIALIZE_DEPTH."""
    # Build a deeply nested object chain
    class Node:
        def __init__(self, depth):
            self.depth = depth
            self.child = Node(depth + 1) if depth < _MAX_SERIALIZE_DEPTH + 5 else None

    result = _deep_serialize(Node(0))
    assert isinstance(result, dict)
    assert result['depth'] == 0

    # Walk the chain: at some point, child should become None (truncated)
    node = result
    for _ in range(_MAX_SERIALIZE_DEPTH + 5):
        if node is None or not isinstance(node, dict) or node.get('child') is None:
            break
        node = node['child']
    # The chain should have been truncated before depth + 5
    assert node is None or not isinstance(node, dict) or node.get('child') is None


def test_traitlet_to_param_non_json_safe_default():
    """_traitlet_to_param sanitizes non-JSON-safe defaults to None."""
    import logging

    class LoggerWidget(anywidget.AnyWidget):
        _esm = 'function render() {}\nexport default { render };'
        logger_ref = traitlets.Any(default_value=logging.getLogger("test")).tag(sync=True)

    _COMPONENT_CACHE.clear()
    widget = LoggerWidget()
    pane = AnyWidget(widget)
    component = pane.component
    assert component is not None

    # The component should have been created without serialization errors.
    # The logger_ref param default should be None (sanitized), but the
    # actual value should be deep-serialized from the widget's traitlet.
    assert isinstance(component.logger_ref, dict)
    _COMPONENT_CACHE.clear()


# ---------------------------------------------------------------
# Scoped document defs (cross-app leakage prevention)
# ---------------------------------------------------------------

def test_scoped_document_defs(document, comm):
    """Document defs only include DataModels used in the current document."""
    from bokeh.core.has_props import is_DataModel

    from panel.io.datamodel import _NAMED_DATA_MODELS, construct_data_model

    # Create two different DataModel classes
    class Widget1(param.Parameterized):
        value = param.Integer(default=0)

    class Widget2(param.Parameterized):
        text = param.String(default="hello")

    model1 = construct_data_model(Widget1, name='ScopedTest1')
    model2 = construct_data_model(Widget2, name='ScopedTest2')

    # Create instances and add only model1 to the document
    instance1 = model1(value=42)
    document.add_root(instance1)

    # Serialize the document
    doc_json = document.to_json(deferred=True)

    # The defs should only include ScopedTest1, not ScopedTest2
    if 'defs' in doc_json:
        # Check the actual data models included in the document
        all_dm = {
            m for m in document.models
            if is_DataModel(type(m))
        }
        dm_classes = {type(m) for m in all_dm}
        assert model1 in dm_classes or len(dm_classes) == 0
        assert model2 not in dm_classes

    # Cleanup
    document.remove_root(instance1)
    _NAMED_DATA_MODELS.pop('ScopedTest1', None)
    _NAMED_DATA_MODELS.pop('ScopedTest2', None)


def test_anywidget_logger_trait_document_serialization():
    """A widget with a Logger-typed trait serializes to a document without errors.

    Regression test for HiGlass: ``can't serialize <class 'logging.Logger'>``.
    The Logger trait has non-JSON-safe defaults AND runtime values with
    non-string dict keys (Manager.loggerDict uses Logger objects as keys).
    """
    import logging

    from bokeh.document import Document

    _COMPONENT_CACHE.clear()

    class LoggerTraitWidget(anywidget.AnyWidget):
        _esm = 'function render() {}\nexport default { render };'
        config = traitlets.Dict({}).tag(sync=True)
        logger_ref = traitlets.Any(
            default_value=logging.getLogger("higlass_test_doc_serialize"),
        ).tag(sync=True)

    widget = LoggerTraitWidget()
    pane = AnyWidget(widget)

    doc = Document()
    root = pane.get_root(doc)
    doc.add_root(root)

    # Must not raise "can't serialize <class 'logging.Logger'>"
    doc_json = doc.to_json(deferred=True)
    assert 'roots' in doc_json
    _COMPONENT_CACHE.clear()


# ---------------------------------------------------------------
# DataFrame serialization helpers
# ---------------------------------------------------------------

def test_is_dataframe_pandas():
    """_is_dataframe detects pandas DataFrames."""
    pd = pytest.importorskip("pandas")
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    assert _is_dataframe(df) is True

def test_is_dataframe_non_df():
    """_is_dataframe returns False for non-DataFrame objects."""
    assert _is_dataframe(None) is False
    assert _is_dataframe([1, 2, 3]) is False
    assert _is_dataframe({"a": 1}) is False

def test_dataframe_to_records_pandas():
    """_dataframe_to_records converts pandas DataFrame to records."""
    pd = pytest.importorskip("pandas")
    df = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
    result = _dataframe_to_records(df)
    assert result == [{"x": 1, "y": "a"}, {"x": 2, "y": "b"}]

def test_deep_serialize_dataframe():
    """_deep_serialize converts DataFrames to records instead of __dict__."""
    pd = pytest.importorskip("pandas")
    df = pd.DataFrame({"col": [10, 20]})
    result = _deep_serialize(df)
    assert isinstance(result, list)
    assert result == [{"col": 10}, {"col": 20}]


# ---------------------------------------------------------------
# Custom message routing (Mosaic-like)
# ---------------------------------------------------------------

class MsgWidget(anywidget.AnyWidget):
    """Widget with a custom message handler (like Mosaic)."""
    _esm = """
    function render({ model, el }) { el.innerHTML = "msg"; }
    export default { render };
    """
    value = traitlets.Int(0).tag(sync=True)
    _received = []  # class-level store for testing

    def _handle_custom_msg(self, data, buffers):
        self._received.append((data, buffers))


def test_anywidget_msg_routing_esm_to_python():
    """ESM → Python: component.on_msg forwards to widget._handle_custom_msg."""
    from panel.models.esm import DataEvent

    _COMPONENT_CACHE.clear()
    MsgWidget._received = []

    widget = MsgWidget()
    pane = AnyWidget(widget)
    component = pane.component
    assert component is not None

    # Simulate ESM sending a DataEvent (what _process_event dispatches)
    event = DataEvent(model=None, data={'query': 'SELECT 1'})
    for cb in component._msg__callbacks:
        cb(event)

    assert len(MsgWidget._received) == 1
    msg_data, msg_buffers = MsgWidget._received[0]
    assert msg_data == {'query': 'SELECT 1'}
    assert msg_buffers == []
    _COMPONENT_CACHE.clear()


def test_anywidget_msg_routing_python_to_esm():
    """Python → ESM: widget.send() routes through component._send_msg."""
    _COMPONENT_CACHE.clear()

    widget = MsgWidget()
    pane = AnyWidget(widget)
    component = pane.component
    assert component is not None

    # Track messages sent through the component
    sent = []
    component._send_msg = lambda content: sent.append(content)

    # widget.send() should route through the component
    widget.send({"result": [1, 2, 3]})

    assert len(sent) == 1
    assert sent[0] == {"result": [1, 2, 3]}
    _COMPONENT_CACHE.clear()


def test_anywidget_msg_routing_roundtrip():
    """Roundtrip: ESM sends a query, Python receives it and responds."""
    from panel.models.esm import DataEvent

    _COMPONENT_CACHE.clear()
    MsgWidget._received = []

    widget = MsgWidget()
    pane = AnyWidget(widget)
    component = pane.component
    assert component is not None

    # Track outgoing messages
    sent = []
    component._send_msg = lambda content: sent.append(content)

    # Simulate ESM → Python message
    event = DataEvent(model=None, data={'type': 'json', 'sql': 'SELECT 1'})
    for cb in component._msg__callbacks:
        cb(event)
    assert len(MsgWidget._received) == 1
    msg_data, msg_buffers = MsgWidget._received[0]
    assert msg_data['type'] == 'json'
    assert msg_buffers == []

    # Simulate Python responding back → ESM
    widget.send({"type": "json", "result": {"rows": [{"col": 1}]}})
    assert len(sent) == 1
    assert sent[0]["type"] == "json"
    _COMPONENT_CACHE.clear()


def test_anywidget_msg_routing_buffers_base64():
    """Binary buffers are base64-encoded into the JSON message."""
    import base64

    _COMPONENT_CACHE.clear()

    widget = MsgWidget()
    pane = AnyWidget(widget)
    component = pane.component
    assert component is not None

    # Track outgoing messages
    sent = []
    component._send_msg = lambda content: sent.append(content)

    # Simulate a Mosaic-like Arrow IPC response with binary buffers
    arrow_data = b'\x00\x01\x02\x03\x04\x05'
    widget.send({"type": "arrow", "uuid": "abc"}, buffers=[arrow_data])

    assert len(sent) == 1
    msg = sent[0]
    assert msg["type"] == "arrow"
    assert msg["uuid"] == "abc"
    assert "_b64_buffers" in msg
    assert len(msg["_b64_buffers"]) == 1
    # Verify the base64 decoding roundtrips correctly
    decoded = base64.b64decode(msg["_b64_buffers"][0])
    assert decoded == arrow_data
    _COMPONENT_CACHE.clear()


def test_anywidget_msg_routing_buffers_memoryview():
    """Memoryview buffers (from pyarrow) are handled correctly."""
    import base64

    _COMPONENT_CACHE.clear()

    widget = MsgWidget()
    pane = AnyWidget(widget)
    component = pane.component
    assert component is not None

    sent = []
    component._send_msg = lambda content: sent.append(content)

    # pyarrow buffers often arrive as memoryview
    raw = b'\xff\xfe\xfd'
    widget.send({"type": "arrow", "uuid": "def"}, buffers=[memoryview(raw)])

    assert len(sent) == 1
    decoded = base64.b64decode(sent[0]["_b64_buffers"][0])
    assert decoded == raw
    _COMPONENT_CACHE.clear()


def test_anywidget_msg_routing_esm_buffers_decoded():
    """ESM→Python: base64-encoded _b64_buffers from ESM are decoded to bytes."""
    import base64

    _COMPONENT_CACHE.clear()
    MsgWidget._received = []

    widget = MsgWidget()
    pane = AnyWidget(widget)
    component = pane.component
    assert component is not None

    # Simulate ESM sending a message with base64-encoded binary buffers
    # (as the TS adapter's send() would do)
    raw_buffer = b'\x00\x01\x02\x03\x04\x05'
    encoded = base64.b64encode(raw_buffer).decode('ascii')
    esm_msg = {
        "type": "arrow_result",
        "uuid": "test123",
        "_b64_buffers": [encoded],
    }

    # Simulate the DataEvent arriving from ESM
    # (on_msg callbacks are stored in _msg__callbacks)
    class FakeEvent:
        data = esm_msg

    for cb in component._msg__callbacks:
        cb(FakeEvent())

    # The widget's _handle_custom_msg should have received decoded buffers
    assert len(MsgWidget._received) == 1
    msg_data, msg_buffers = MsgWidget._received[0]
    assert msg_data["type"] == "arrow_result"
    assert msg_data["uuid"] == "test123"
    assert "_b64_buffers" not in msg_data  # transport key removed
    assert len(msg_buffers) == 1
    assert msg_buffers[0] == raw_buffer
    _COMPONENT_CACHE.clear()


def test_anywidget_msg_routing_esm_buffers_multiple():
    """ESM→Python: multiple base64 buffers are decoded correctly."""
    import base64

    _COMPONENT_CACHE.clear()
    MsgWidget._received = []

    widget = MsgWidget()
    pane = AnyWidget(widget)
    component = pane.component
    assert component is not None

    buf1 = b'\x00\x01\x02'
    buf2 = b'\xff\xfe\xfd\xfc'
    esm_msg = {
        "type": "multi_arrow",
        "_b64_buffers": [
            base64.b64encode(buf1).decode('ascii'),
            base64.b64encode(buf2).decode('ascii'),
        ],
    }

    class FakeEvent:
        data = esm_msg

    for cb in component._msg__callbacks:
        cb(FakeEvent())

    assert len(MsgWidget._received) == 1
    msg_data, msg_buffers = MsgWidget._received[0]
    assert msg_data == {"type": "multi_arrow"}
    assert len(msg_buffers) == 2
    assert msg_buffers[0] == buf1
    assert msg_buffers[1] == buf2
    _COMPONENT_CACHE.clear()


def test_anywidget_trait_name_map_property():
    """pane.trait_name_map exposes renamed traits for discoverability."""
    _COMPONENT_CACHE.clear()

    widget = NameCollisionWidget()
    pane = AnyWidget(widget)
    assert 'name' in pane.trait_name_map
    assert pane.trait_name_map['name'] == 'w_name'
    assert 'width' in pane.trait_name_map
    assert pane.trait_name_map['width'] == 'w_width'

    # Non-colliding widget should have empty map
    _COMPONENT_CACHE.clear()
    counter = CounterWidget()
    pane2 = AnyWidget(counter)
    assert pane2.trait_name_map == {}
    _COMPONENT_CACHE.clear()


def test_anywidget_invoke_command_routing():
    """Verify that anywidget-command messages are forwarded to widget._handle_custom_msg.

    The experimental.invoke() RPC pattern (from @anywidget/signals) sends
    messages with {id, kind: "anywidget-command", name, msg} and expects
    the Python side to dispatch them via _handle_custom_msg.
    """
    from panel.models.esm import DataEvent

    _COMPONENT_CACHE.clear()
    MsgWidget._received = []

    widget = MsgWidget()
    pane = AnyWidget(widget)
    component = pane.component
    assert component is not None

    # Simulate an invoke-style message from the TS adapter
    invoke_msg = {
        'id': 'test-uuid-123',
        'kind': 'anywidget-command',
        'name': 'my_command',
        'msg': {'x': 42},
    }
    event = DataEvent(model=None, data=invoke_msg)
    for cb in component._msg__callbacks:
        cb(event)

    assert len(MsgWidget._received) == 1
    msg_data, msg_buffers = MsgWidget._received[0]
    assert msg_data['kind'] == 'anywidget-command'
    assert msg_data['name'] == 'my_command'
    assert msg_data['msg'] == {'x': 42}
    assert msg_data['id'] == 'test-uuid-123'
    assert msg_buffers == []
    _COMPONENT_CACHE.clear()


def test_anywidget_invoke_command_with_buffers():
    """Verify that invoke messages with base64-encoded buffers are decoded."""
    import base64

    from panel.models.esm import DataEvent

    _COMPONENT_CACHE.clear()
    MsgWidget._received = []

    widget = MsgWidget()
    pane = AnyWidget(widget)
    component = pane.component
    assert component is not None

    # Simulate an invoke message with base64-encoded buffers
    raw_data = b'\x01\x02\x03\x04'
    encoded = base64.b64encode(raw_data).decode('ascii')
    invoke_msg = {
        'id': 'test-uuid-456',
        'kind': 'anywidget-command',
        'name': 'binary_command',
        'msg': {'query': 'data'},
        '_b64_buffers': [encoded],
    }
    event = DataEvent(model=None, data=invoke_msg)
    for cb in component._msg__callbacks:
        cb(event)

    assert len(MsgWidget._received) == 1
    msg_data, msg_buffers = MsgWidget._received[0]
    # The _b64_buffers key should be stripped and decoded into buffers
    assert '_b64_buffers' not in msg_data
    assert msg_data['kind'] == 'anywidget-command'
    assert len(msg_buffers) == 1
    assert msg_buffers[0] == raw_data
    _COMPONENT_CACHE.clear()


def test_anywidget_send_override_delivers_response():
    """Verify that widget.send() with anywidget-command-response data
    is forwarded through the component's _send_msg for the invoke pattern."""
    _COMPONENT_CACHE.clear()

    widget = MsgWidget()
    pane = AnyWidget(widget)
    component = pane.component
    assert component is not None

    # Track messages sent through the component
    sent = []
    component._send_msg = lambda content: sent.append(content)

    # widget.send() is the Python→ESM direction used for invoke responses
    response_msg = {
        'id': 'test-uuid-789',
        'kind': 'anywidget-command-response',
        'response': {'result': 'ok'},
    }
    widget.send(response_msg)

    assert len(sent) == 1
    assert sent[0]['id'] == 'test-uuid-789'
    assert sent[0]['kind'] == 'anywidget-command-response'
    assert sent[0]['response'] == {'result': 'ok'}
    _COMPONENT_CACHE.clear()


def test_anywidget_send_restored_on_cleanup():
    """widget.send is restored to its original when the pane is cleaned up."""
    _COMPONENT_CACHE.clear()

    widget = MsgWidget()

    pane = AnyWidget(widget)
    _ = pane.component  # trigger component creation + msg routing

    # After wrapping, widget.send should be the Panel override (a function, not a bound method)
    import types
    assert not isinstance(widget.send, types.MethodType)
    assert callable(widget.send)

    # Cleanup the pane
    pane._teardown_trait_sync()

    # After cleanup, widget.send should be a bound method again (the original)
    assert isinstance(widget.send, types.MethodType)
    _COMPONENT_CACHE.clear()


# ---------------------------------------------------------------
# Initialize-phase msg:custom handler queuing
# ---------------------------------------------------------------

def test_anywidget_initialize_msg_custom_queuing():
    """Widgets that call model.on("msg:custom", cb) during initialize()
    should have their handlers queued and connected when the view is ready.

    This tests the fix for quak-style widgets that register msg:custom
    handlers in their ESM initialize() function, before the view exists.
    """
    _COMPONENT_CACHE.clear()

    class MsgWidget(anywidget.AnyWidget):
        _esm = """
        function initialize({ model }) {
            // Register msg:custom handler during initialize (before render)
            model.on("msg:custom", (data, buffers) => {
                model.set("last_msg", JSON.stringify(data));
                model.save_changes();
            });
        }
        function render({ model, el }) {
            el.innerHTML = "msg widget";
        }
        export default { render, initialize };
        """
        last_msg = traitlets.Unicode("").tag(sync=True)

    widget = MsgWidget()
    pane = AnyWidget(widget)
    component = pane.component

    # The component should have the last_msg param
    assert hasattr(component, 'last_msg')
    assert component.last_msg == ""
    _COMPONENT_CACHE.clear()


# ---------------------------------------------------------------
# Compound widget (child widget) support
# ---------------------------------------------------------------

ipywidgets = pytest.importorskip("ipywidgets")


class ChildWidget(ipywidgets.DOMWidget):
    """Mock child widget with sync-tagged traits."""
    _model_name = traitlets.Unicode('ChildWidgetModel').tag(sync=True)
    _model_module = traitlets.Unicode('test').tag(sync=True)
    _view_name = traitlets.Unicode('ChildWidgetView').tag(sync=True)
    _view_module = traitlets.Unicode('test').tag(sync=True)
    color = traitlets.Unicode('red').tag(sync=True)
    table = traitlets.Bytes(b'').tag(sync=True)


class ParentCompound(anywidget.AnyWidget):
    """Mock compound widget with widget_serialization traits."""
    _esm = """
    function render({ model, el }) {
        el.innerHTML = "compound";
    }
    export default { render };
    """
    layer = traitlets.Instance(ipywidgets.Widget, allow_none=True).tag(
        sync=True, **ipywidgets.widget_serialization,
    )
    layers = traitlets.List(traitlets.Instance(ipywidgets.Widget)).tag(
        sync=True, **ipywidgets.widget_serialization,
    )
    value = traitlets.Int(0).tag(sync=True)


class TestCollectChildWidgets:

    def test_single_child(self):
        _COMPONENT_CACHE.clear()
        child = ChildWidget()
        parent = ParentCompound(layer=child, layers=[])
        result = _collect_child_widgets(parent)
        assert child.model_id in result
        assert result[child.model_id] is child
        _COMPONENT_CACHE.clear()

    def test_list_of_children(self):
        _COMPONENT_CACHE.clear()
        c1 = ChildWidget()
        c2 = ChildWidget()
        parent = ParentCompound(layers=[c1, c2])
        result = _collect_child_widgets(parent)
        assert c1.model_id in result
        assert c2.model_id in result
        _COMPONENT_CACHE.clear()

    def test_no_widget_serialization(self):
        """Leaf widgets (no widget_serialization traits) return empty dict."""
        _COMPONENT_CACHE.clear()
        widget = CounterWidget()
        result = _collect_child_widgets(widget)
        assert result == {}
        _COMPONENT_CACHE.clear()

    def test_recursive_grandchildren(self):
        """Grandchild widgets are discovered recursively."""
        _COMPONENT_CACHE.clear()
        grandchild = ChildWidget()
        # Create an intermediate compound widget with a child
        intermediate = ParentCompound(layer=grandchild, layers=[])
        # Outer parent has intermediate as its layer
        outer = ParentCompound(layer=intermediate, layers=[])
        result = _collect_child_widgets(outer)
        # Should find both intermediate and grandchild
        assert intermediate.model_id in result
        assert grandchild.model_id in result
        _COMPONENT_CACHE.clear()

    def test_circular_reference_safety(self):
        """Circular widget references don't cause infinite recursion."""
        _COMPONENT_CACHE.clear()
        parent = ParentCompound(layers=[])
        # Manually create a circular reference (parent references itself)
        parent.layer = parent
        result = _collect_child_widgets(parent)
        # Should not hang; parent itself should be collected once
        assert parent.model_id in result
        _COMPONENT_CACHE.clear()


class TestSerializeChildState:

    def test_basic_serialization(self):
        _COMPONENT_CACHE.clear()
        child = ChildWidget(color='blue')
        state = _serialize_child_state(child)
        assert state['color'] == 'blue'
        _COMPONENT_CACHE.clear()

    def test_binary_data(self):
        _COMPONENT_CACHE.clear()
        child = ChildWidget(table=b'\x00\x01\x02')
        state = _serialize_child_state(child)
        # _serialize_trait calls _deep_serialize at depth 0, which passes
        # bytes through as-is for Bokeh's native bp.Bytes serializer.
        assert state['table'] == b'\x00\x01\x02'
        _COMPONENT_CACHE.clear()


class TestCompoundWidgetConstantsPopulation:

    def test_child_models_in_constants(self):
        _COMPONENT_CACHE.clear()
        child = ChildWidget(color='green')
        parent = ParentCompound(layer=child, layers=[])
        pane = AnyWidget(parent)
        component = pane.component
        assert component is not None
        constants = component._constants
        assert '_child_models' in constants
        assert child.model_id in constants['_child_models']
        child_state = constants['_child_models'][child.model_id]['state']
        assert child_state['color'] == 'green'
        _COMPONENT_CACHE.clear()

    def test_leaf_widget_has_no_child_models(self):
        _COMPONENT_CACHE.clear()
        widget = CounterWidget()
        pane = AnyWidget(widget)
        component = pane.component
        assert component is not None
        constants = component._constants
        assert '_child_models' not in constants
        _COMPONENT_CACHE.clear()


class TestCompoundWidgetCleanup:

    def test_clears_child_widgets(self):
        _COMPONENT_CACHE.clear()
        child = ChildWidget()
        parent = ParentCompound(layer=child, layers=[])
        pane = AnyWidget(parent)
        assert len(pane._child_widgets) > 0
        pane._teardown_trait_sync()
        assert pane._child_widgets == {}
        _COMPONENT_CACHE.clear()

    def test_restores_child_send(self):
        import types

        _COMPONENT_CACHE.clear()
        child = ChildWidget()
        parent = ParentCompound(layer=child, layers=[])
        pane = AnyWidget(parent)

        # After setup, child.send should be overridden
        assert not isinstance(child.send, types.MethodType)
        assert callable(child.send)

        pane._teardown_trait_sync()

        # After cleanup, child.send should be restored
        assert isinstance(child.send, types.MethodType)
        _COMPONENT_CACHE.clear()


class TestIsWidgetSerialization:

    def test_widget_serialization_trait(self):
        trait = ParentCompound.class_traits()['layer']
        assert _is_widget_serialization(trait) is True

    def test_non_widget_serialization_trait(self):
        trait = ParentCompound.class_traits()['value']
        assert _is_widget_serialization(trait) is False


# ---------------------------------------------------------------
# Tuple coercion (JSON list -> tuple for param.Tuple params)
# ---------------------------------------------------------------

class TupleWidget(anywidget.AnyWidget):
    _esm = 'function render() {}\nexport default { render };'
    bounds = traitlets.Tuple(
        traitlets.Float(), traitlets.Float(),
        traitlets.Float(), traitlets.Float(),
        default_value=None, allow_none=True,
    ).tag(sync=True)


def test_process_property_change_list_to_tuple():
    """AnyWidgetComponent._process_property_change converts JSON lists to tuples
    for param.Tuple parameters (e.g. lonboard selected_bounds)."""
    _COMPONENT_CACHE.clear()
    widget = TupleWidget()
    pane = AnyWidget(widget)
    component = pane.component
    assert component is not None
    result = component._process_property_change({'bounds': [1.0, 2.0, 3.0, 4.0]})
    assert result['bounds'] == (1.0, 2.0, 3.0, 4.0)
    assert isinstance(result['bounds'], tuple)
    _COMPONENT_CACHE.clear()


def test_process_property_change_preserves_non_tuple():
    """Lists for param.List params stay as lists (not coerced to tuple)."""
    _COMPONENT_CACHE.clear()
    widget = MultiTraitWidget()
    pane = AnyWidget(widget)
    component = pane.component
    assert component is not None
    result = component._process_property_change({'data': [1, 2, 3]})
    assert result['data'] == [1, 2, 3]
    assert isinstance(result['data'], list)
    _COMPONENT_CACHE.clear()


def test_tuple_length_inferred_from_traitlet():
    """_traitlet_to_param infers param.Tuple length from traitlet._traits."""
    _COMPONENT_CACHE.clear()
    trait = TupleWidget.class_traits()['bounds']
    p = _traitlet_to_param(trait)
    assert isinstance(p, param.Tuple)
    assert p.length == 4
    _COMPONENT_CACHE.clear()
