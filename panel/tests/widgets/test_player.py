from panel.models import Player as BkPlayer
from panel.widgets import DiscretePlayer


def test_discrete_player(document, comm):
    discrete_player = DiscretePlayer(name='DiscretePlayer', value=1.,
                                     options=[0.1, 1., 10, 100])

    widget = discrete_player.get_root(document, comm=comm)

    assert isinstance(widget, BkPlayer)
    assert widget.value == 1
    assert widget.start == 0
    assert widget.end == 3
    assert widget.step == 1

    widget.value = 2
    discrete_player._process_events({'value': 2})
    assert discrete_player.value == 10

    discrete_player.value = 100
    assert widget.value == 3
