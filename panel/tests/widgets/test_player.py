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


def test_player_loop_policy_not_in_loop_options(document, comm):
    player = DiscretePlayer(name='Player', loop_policy='once', visible_loop_options=['loop', 'reflect'])
    assert player.loop_policy == 'loop'
    assert player.visible_loop_options == ['loop', 'reflect']


def test_player_loop_policy_with_no_loop_options(document, comm):
    player = DiscretePlayer(name='Player', loop_policy='loop', visible_loop_options=[])
    assert player.loop_policy == 'loop'
    assert player.visible_loop_options == []
