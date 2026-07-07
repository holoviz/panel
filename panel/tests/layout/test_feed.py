import pytest

from panel import Feed


def test_feed_init():
    feed = Feed()
    assert feed.height == 300
    assert feed.scroll


@pytest.mark.parametrize(
    ("params", "expected_height"),
    [
        ({}, 300),
        ({"height": 250}, 250),
        ({"max_height": 400}, None),
        ({"min_height": 500}, 300),
        ({"scroll": False}, None),
    ],
    ids=["no_bounds", "explicit_height", "max_height", "min_height_only", "scroll_false"],
)
def test_feed_default_height_guard(params, expected_height):
    # A scrolling Feed needs a bounding height (height/max_height) to clip its
    # viewport; min_height only sets a floor, so a min_height-only Feed must
    # still receive the default height to prevent runaway loading (#8661). A
    # non-scrolling Feed renders all objects and needs no default height.
    feed = Feed(**params)
    assert feed.height == expected_height


def test_feed_scroll_false_renders_all():
    # A non-scrolling Feed cannot clip a viewport, so it renders every object
    # instead of virtualizing; visible_range is measured against the page
    # viewport on the frontend (#8661).
    feed = Feed(*list(range(100)), scroll=False)
    assert feed._synced_range == (0, 100)


def test_feed_set_objects():
    feed = Feed(height=100)
    feed.objects = list(range(1000))
    assert [o.object for o in feed.objects] == list(range(1000))
