"""
Spacer components to add horizontal or vertical space to a layout.
"""

import param

from bokeh.models import Div as BkDiv, Spacer as BkSpacer

from ..reactive import Reactive


class Spacer(Reactive):
    """
    The `Spacer` layout is a very versatile component which makes it easy to
    put fixed or responsive spacing between objects.

    Like all other components spacers support both absolute and responsive
    sizing modes.

    Reference: https://panel.holoviz.org/user_guide/Customization.html#spacers

    :Example:

    >>> pn.Row(
    ...    1, pn.Spacer(width=200),
    ...    2, pn.Spacer(width=100),
    ...    3
    ... )
    """

    _bokeh_model = BkSpacer

    def _get_model(self, doc, root=None, parent=None, comm=None):
        properties = self._process_param_change(self._init_params())
        model = self._bokeh_model(**properties)
        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        return model


class VSpacer(Spacer):
    """
    The `VSpacer` layout provides responsive vertical spacing.

    Using this component we can space objects equidistantly in a layout and
    allow the empty space to shrink when the browser is resized.

    Reference: https://panel.holoviz.org/user_guide/Customization.html#spacers

    :Example:

    >>> pn.Column(
    ...     pn.layout.VSpacer(), 'Item 1',
    ...     pn.layout.VSpacer(), 'Item 2',
    ...     pn.layout.VSpacer()
    ... )
    """

    sizing_mode = param.Parameter(default='stretch_height', readonly=True)


class HSpacer(Spacer):
    """
    The `HSpacer` layout provides responsive vertical spacing.

    Using this component we can space objects equidistantly in a layout and
    allow the empty space to shrink when the browser is resized.

    Reference: https://panel.holoviz.org/user_guide/Customization.html#spacers

    :Example:

    >>> pn.Row(
    ...     pn.layout.HSpacer(), 'Item 1',
    ...     pn.layout.HSpacer(), 'Item 2',
    ...     pn.layout.HSpacer()
    ... )
    """

    sizing_mode = param.Parameter(default='stretch_width', readonly=True)


class Divider(Reactive):
    """
    A `Divider` draws a horizontal rule (a `<hr>` tag in HTML) to separate
    multiple components in a layout. It automatically spans the full width of
    the container.

    Reference: https://panel.holoviz.org/reference/layouts/Divider.html

    :Example:

    >>> pn.Column(
    ...     '# Lorem Ipsum',
    ...     pn.layout.Divider(),
    ...     'A very long text... '
    >>> )
    """

    width_policy = param.ObjectSelector(default="fit", readonly=True)

    _bokeh_model = BkDiv

    def _get_model(self, doc, root=None, parent=None, comm=None):
        properties = self._process_param_change(self._init_params())
        properties['style'] = {'width': '100%', 'height': '100%'}
        model = self._bokeh_model(text='<hr style="margin: 0px">', **properties)
        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        return model
