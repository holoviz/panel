from pathlib import Path

import param

from ..reactive import ReactiveHTML
from .base import ListLike


class FlexBox(ListLike, ReactiveHTML):

    align_content = param.Selector(default='flex-start', objects=[
        'normal', 'flex-start', 'flex-end', 'center', 'space-between',
        'space-around', 'space-evenly', 'stretch', 'start', 'end',
        'baseline', 'first baseline', 'last baseline'], doc="""
        Defines how a flex container's lines align when there is extra
        space in the cross-axis.""")

    align_items = param.Selector(default='flex-start', objects=[
        'stretch', 'flex-start', 'flex-end', 'center', 'baseline',
        'first baseline', 'last baseline', 'start', 'end',
        'self-start', 'self-end'], doc="""
        Defines the default behavior for how flex items are laid
        out along the cross axis on the current line.""")

    flex_direction = param.Selector(default='row', objects=[
        'row', 'row-reverse', 'column', 'column-reverse'], doc="""
        This establishes the main-axis, thus defining the direction
        flex items are placed in the flex container.""")

    flex_wrap = param.Selector(default='wrap', objects=[
        'nowrap', 'wrap', 'wrap-reverse'], doc="""
        Whether and how to wrap items in the flex container.""")

    justify_content = param.Selector(default='flex-start', objects=[
        'flex-start', 'flex-end', 'center', 'space-between', 'space-around',
        'space-evenly', 'start', 'end', 'left', 'right'], doc="""
        Defines the alignment along the main axis.""")

    _template = (Path(__file__).parent / 'flexbox.html').read_text('utf-8')

    def __init__(self, *objects, **params):
        if 'sizing_mode' not in params:
            direction = params.get('flex_direction', self.flex_direction)
            if direction.startswith('row'):
                params['sizing_mode'] = 'stretch_width'
            else:
                params['sizing_mode'] = 'stretch_height'
        super().__init__(objects=list(objects), **params)

