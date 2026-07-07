from panel import Feed


def test_feed_init():
    feed = Feed()
    assert feed.height == 300
    assert feed.scroll


def test_feed_scroll_false_renders_all():
    """A non-scrolling Feed cannot clip a viewport, so it renders every object
    instead of virtualizing; visible_range is measured against the page viewport
    on the frontend (#8661)."""
    feed = Feed(*list(range(100)), scroll=False)
    assert feed._synced_range == (0, 100)


def test_feed_scroll_false_no_default_height():
    """A non-scrolling Feed must not receive the default height, which would clip
    it to a fixed viewport rather than letting the page scroll (#8661)."""
    assert Feed(scroll=False).height is None


def test_feed_set_objects():
    feed = Feed(height=100)
    feed.objects = list(range(1000))
    assert [o.object for o in feed.objects] == list(range(1000))
