import pytest

from panel.layout import Overlay
from panel.pane import Markdown


@pytest.fixture
def panels():
    return Markdown('Legend'), Markdown('Controls'), Markdown('Guide')


#-----------------------------------------------------------------------------
# Construction
#-----------------------------------------------------------------------------

def test_overlay_empty():
    overlay = Overlay()

    assert overlay.objects == []
    assert overlay.anchors == []
    assert overlay.base is None


def test_overlay_margin_default():
    assert Overlay().margin == 0


def test_overlay_named_anchor_construction(panels):
    legend, controls, _ = panels
    overlay = Overlay(('top-left', legend), ('top-right', controls))

    assert [o.object for o in overlay.objects] == ['Legend', 'Controls']
    assert overlay.anchors == ['top-left', 'top-right']


def test_overlay_coordinate_construction(panels):
    legend, _, _ = panels
    overlay = Overlay(((24, 80), legend))

    assert overlay.anchors == [(24, 80)]


def test_overlay_percentage_coordinate_construction(panels):
    legend, _, _ = panels
    overlay = Overlay((("50%", "10%"), legend))

    assert overlay.anchors == [("50%", "10%")]


def test_overlay_mixed_coordinate_construction(panels):
    legend, _, _ = panels
    overlay = Overlay(((24, "10%"), legend))

    assert overlay.anchors == [(24, "10%")]


def test_overlay_mixed_construction(panels):
    legend, controls, guide = panels
    overlay = Overlay(
        ('top-left', legend),
        ((24, 80), controls),
        ('bottom-right', guide),
    )

    assert overlay.anchors == ['top-left', (24, 80), 'bottom-right']


def test_overlay_base_via_constructor(panels):
    legend, _, _ = panels
    base = Markdown('Map')
    overlay = Overlay(('top-left', legend), base=base)

    assert overlay.base is base


def test_overlay_wraps_bare_python_objects():
    overlay = Overlay(('top-left', 'Legend'))

    assert overlay.objects[0].object == 'Legend'
    assert overlay.anchors == ['top-left']


#-----------------------------------------------------------------------------
# sizing_mode/margin are inherited from `base` unless set explicitly
#-----------------------------------------------------------------------------

def test_overlay_inherits_sizing_mode_and_margin_from_base():
    base = Markdown('Map', sizing_mode='stretch_both', margin=7)
    overlay = Overlay(('top-left', Markdown('Legend')), base=base)

    assert overlay.sizing_mode == 'stretch_both'
    assert overlay.margin == 7


def test_overlay_explicit_sizing_mode_and_margin_win_over_base():
    base = Markdown('Map', sizing_mode='stretch_both', margin=7)
    overlay = Overlay(
        ('top-left', Markdown('Legend')), base=base,
        sizing_mode='fixed', margin=3,
    )

    assert overlay.sizing_mode == 'fixed'
    assert overlay.margin == 3


def test_overlay_no_base_keeps_own_defaults():
    overlay = Overlay(('top-left', Markdown('Legend')))

    assert overlay.sizing_mode is None
    assert overlay.margin == 0


def test_overlay_base_sizing_mode_none_does_not_force_fixed():
    # Only inherit an actual value -- a base with sizing_mode=None
    # (the common case) shouldn't push the Overlay to some other mode.
    base = Markdown('Map', margin=9)
    overlay = Overlay(('top-left', Markdown('Legend')), base=base)

    assert overlay.sizing_mode is None
    assert overlay.margin == 9


def test_overlay_base_swap_updates_uninherited_sizing():
    base1 = Markdown('Map 1', sizing_mode='stretch_width', margin=2)
    base2 = Markdown('Map 2', sizing_mode='stretch_height', margin=4)
    overlay = Overlay(('top-left', Markdown('Legend')), base=base1)
    assert overlay.sizing_mode == 'stretch_width'
    assert overlay.margin == 2

    overlay.base = base2

    assert overlay.sizing_mode == 'stretch_height'
    assert overlay.margin == 4


def test_overlay_pinned_sizing_mode_survives_base_swap():
    base1 = Markdown('Map 1', sizing_mode='stretch_width')
    base2 = Markdown('Map 2', sizing_mode='stretch_height')
    overlay = Overlay(('top-left', Markdown('Legend')), base=base1)

    overlay.sizing_mode = 'fixed'  # user pins it explicitly
    overlay.base = base2

    assert overlay.sizing_mode == 'fixed'


def test_overlay_pinned_margin_survives_base_swap():
    base1 = Markdown('Map 1', margin=2)
    base2 = Markdown('Map 2', margin=4)
    overlay = Overlay(('top-left', Markdown('Legend')), base=base1, margin=1)

    overlay.base = base2

    assert overlay.margin == 1


#-----------------------------------------------------------------------------
# Validation
#-----------------------------------------------------------------------------

def test_overlay_bare_object_raises(panels):
    legend, _, _ = panels
    with pytest.raises(ValueError, match=r'must be \(anchor, object\) tuples'):
        Overlay(legend)


def test_overlay_invalid_anchor_raises(panels):
    legend, _, _ = panels
    with pytest.raises(ValueError, match='invalid anchor'):
        Overlay(('somewhere', legend))


def test_overlay_invalid_coordinate_length_raises(panels):
    legend, _, _ = panels
    with pytest.raises(ValueError, match='invalid anchor'):
        Overlay(((1, 2, 3), legend))


def test_overlay_invalid_coordinate_type_raises(panels):
    legend, _, _ = panels
    with pytest.raises(ValueError, match='invalid anchor'):
        Overlay(((legend, 2), legend))


def test_overlay_duplicate_named_anchor_raises(panels):
    legend, controls, _ = panels
    with pytest.raises(ValueError, match="duplicate anchor: 'top-left'"):
        Overlay(('top-left', legend), ('top-left', controls))


def test_overlay_duplicate_coordinate_allowed(panels):
    legend, controls, _ = panels
    overlay = Overlay(((0, 0), legend), ((0, 0), controls))

    assert overlay.anchors == [(0, 0), (0, 0)]


def test_overlay_append_raises_on_duplicate_anchor(panels):
    legend, controls, _ = panels
    overlay = Overlay(('top-left', legend))

    with pytest.raises(ValueError, match="duplicate anchor: 'top-left'"):
        overlay.append(('top-left', controls))


def test_overlay_objects_direct_assignment_requires_valid_anchor(panels):
    # Bypassing the (anchor, obj) tuple API by setting `.objects`
    # directly isn't supported -- there's no anchor to fall back to,
    # so this is expected to raise rather than silently guess one.
    legend, controls, _ = panels
    overlay = Overlay(('top-left', legend))

    with pytest.raises(ValueError, match='invalid anchor'):
        overlay.objects = [legend, controls]


#-----------------------------------------------------------------------------
# List-like API keeps `.anchors` aligned with `.objects`
#-----------------------------------------------------------------------------

def test_overlay_append_keeps_anchors_aligned(panels):
    legend, controls, _ = panels
    overlay = Overlay(('top-left', legend))
    overlay.append(('bottom-right', controls))

    assert overlay.anchors == ['top-left', 'bottom-right']
    assert [o.object for o in overlay.objects] == ['Legend', 'Controls']


def test_overlay_insert_keeps_anchors_aligned(panels):
    legend, controls, guide = panels
    overlay = Overlay(('top-left', legend), ('bottom-right', guide))
    overlay.insert(1, ('top-right', controls))

    assert overlay.anchors == ['top-left', 'top-right', 'bottom-right']


def test_overlay_extend_keeps_anchors_aligned(panels):
    legend, controls, guide = panels
    overlay = Overlay(('top-left', legend))
    overlay.extend([('top-right', controls), ('bottom-right', guide)])

    assert overlay.anchors == ['top-left', 'top-right', 'bottom-right']


def test_overlay_setitem_updates_anchor(panels):
    legend, _, _ = panels
    overlay = Overlay(('top-left', legend))
    overlay[0] = ('bottom-right', legend)

    assert overlay.anchors == ['bottom-right']
    assert overlay.objects[0].object == 'Legend'


def test_overlay_setitem_slice_keeps_anchors_aligned(panels):
    legend, controls, guide = panels
    overlay = Overlay(('top-left', legend), ('top-right', controls))
    overlay[0:2] = [('bottom-left', guide), ('bottom-right', legend)]

    assert overlay.anchors == ['bottom-left', 'bottom-right']


def test_overlay_pop_keeps_anchors_aligned(panels):
    legend, controls, _ = panels
    overlay = Overlay(('top-left', legend), ('top-right', controls))
    overlay.pop(0)

    assert overlay.anchors == ['top-right']
    assert len(overlay.objects) == 1


def test_overlay_remove_keeps_anchors_aligned(panels):
    legend, controls, _ = panels
    overlay = Overlay(('top-left', legend), ('top-right', controls))
    overlay.remove(controls)

    assert overlay.anchors == ['top-left']


def test_overlay_reverse_keeps_anchors_aligned(panels):
    legend, controls, _ = panels
    overlay = Overlay(('top-left', legend), ('top-right', controls))
    overlay.reverse()

    assert overlay.anchors == ['top-right', 'top-left']


def test_overlay_clear():
    overlay = Overlay(('top-left', Markdown('Legend')))
    overlay.clear()

    assert overlay.objects == []
    assert overlay.anchors == []


def test_overlay_clone_preserves_params(panels):
    legend, _, _ = panels
    base = Markdown('Map')
    overlay = Overlay(('top-left', legend), base=base, sizing_mode='stretch_both')
    cloned = overlay.clone()

    assert cloned is not overlay
    assert cloned.base is base
    assert cloned.sizing_mode == 'stretch_both'
    assert cloned.anchors == ['top-left']


def test_overlay_clone_with_new_objects(panels):
    legend, controls, _ = panels
    overlay = Overlay(('top-left', legend), base=Markdown('Map'))
    cloned = overlay.clone(('bottom-right', controls))

    assert cloned.anchors == ['bottom-right']
    assert cloned.base is overlay.base


def test_overlay_add_combines_anchors(panels):
    legend, controls, _ = panels
    overlay1 = Overlay(('top-left', legend))
    overlay2 = Overlay(('top-right', controls))
    combined = overlay1 + overlay2

    assert combined.anchors == ['top-left', 'top-right']


def test_overlay_iadd_combines_anchors(panels):
    legend, controls, _ = panels
    overlay = Overlay(('top-left', legend))
    overlay += [('top-right', controls)]

    assert overlay.anchors == ['top-left', 'top-right']


#-----------------------------------------------------------------------------
# Model / rendering
#-----------------------------------------------------------------------------

def test_overlay_get_root(document, comm):
    from panel.models import ReactiveESM as BkReactiveESM

    legend = Markdown('Legend')
    base = Markdown('Map')
    overlay = Overlay(('top-left', legend), base=base)

    model = overlay.get_root(document, comm=comm)

    assert isinstance(model, BkReactiveESM)
    assert model.data._anchors == ['top-left']
    assert len(model.data.objects) == 1
    assert model.data.base is not None


def test_overlay_get_root_no_base(document, comm):
    overlay = Overlay(('top-left', Markdown('Legend')))

    model = overlay.get_root(document, comm=comm)

    assert model.data.base is None


def test_overlay_get_root_no_objects(document, comm):
    overlay = Overlay(base=Markdown('Map'))

    model = overlay.get_root(document, comm=comm)

    assert model.data.objects == []
    assert model.data._anchors == []
    assert model.data.base is not None


def test_overlay_margin_is_top_level_model_property(document, comm):
    overlay = Overlay()

    model = overlay.get_root(document, comm=comm)

    # margin must stay a genuine bokeh LayoutDOM property (applied by
    # Bokeh's own layout/CSS machinery), not get rerouted into the
    # ESM `data` submodel, or the full-bleed default would be inert.
    assert model.margin == 0


def test_overlay_reactive_anchor_update(document, comm):
    legend = Markdown('Legend')
    overlay = Overlay(('top-left', legend))
    model = overlay.get_root(document, comm=comm)

    overlay[0] = ('bottom-right', legend)

    assert model.data._anchors == ['bottom-right']


def test_overlay_reactive_base_swap(document, comm):
    base1 = Markdown('Map 1')
    base2 = Markdown('Map 2')
    overlay = Overlay(base=base1)
    model = overlay.get_root(document, comm=comm)
    base1_model = model.data.base

    overlay.base = base2

    assert model.data.base is not base1_model


def test_overlay_reactive_objects_append(document, comm):
    legend = Markdown('Legend')
    controls = Markdown('Controls')
    overlay = Overlay(('top-left', legend))
    model = overlay.get_root(document, comm=comm)

    overlay.append(('top-right', controls))

    assert len(model.data.objects) == 2
    assert model.data._anchors == ['top-left', 'top-right']
