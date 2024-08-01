from panel import Feed


def test_feed_init(document, comm):
    feed = Feed()
    assert feed.height == 300
    assert feed.scroll


def test_feed_set_objects(document, comm):
    feed = Feed(height=100)
    feed.objects = list(range(1000))
    assert [o.object for o in feed.objects] == list(range(1000))
