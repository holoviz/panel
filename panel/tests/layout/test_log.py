from panel.layout.log import Log


def test_log_init(document, comm):
    log = Log()
    assert log.height == 300
    assert log.scroll


def test_log_set_objects(document, comm):
    log = Log(height=100)
    log.objects = list(range(1000))
    assert log.objects == list(range(1000))
