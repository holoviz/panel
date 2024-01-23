from panel import Feed


def test_log_init(document, comm):
    log = Feed()
    assert log.height == 300
    assert log.scroll


def test_log_set_objects(document, comm):
    log = Feed(height=100)
    log.objects = list(range(1000))
    assert log.objects == list(range(1000))
