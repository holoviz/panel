from panel import Modal


def test_modal_construct():
    modal=Modal("component", "another component")

    modal.show_close_button = False
    modal.is_open=True
    modal.param.trigger("close")
    modal.param.trigger("open")
