"""
Defines the Button and button-like widgets which allow triggering
events or merely toggling between on-off states.
"""
from __future__ import annotations

from typing import (
    TYPE_CHECKING, Any, Callable, ClassVar, Dict, List, Mapping, Optional,
    Type,
)

import param

from bokeh.events import ButtonClick, MenuItemClick
from bokeh.models import (
    Button as _BkButton, Dropdown as _BkDropdown, Toggle as _BkToggle,
)
from bokeh.models.ui import SVGIcon, TablerIcon

from ..io.resources import CDN_DIST
from ..links import Callback
from .base import Widget

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm

    from ..links import JSLinkTarget, Link


BUTTON_TYPES: List[str] = ['default', 'primary', 'success', 'warning', 'danger', 'light']
BUTTON_STYLES: List[str] = ['solid', 'outline']

class _ButtonBase(Widget):

    button_type = param.ObjectSelector(default='default', objects=BUTTON_TYPES, doc="""
        A button theme; should be one of 'default' (white), 'primary'
        (blue), 'success' (green), 'info' (yellow), 'light' (light),
        or 'danger' (red).""")

    button_style = param.ObjectSelector(default='solid', objects=BUTTON_STYLES, doc="""
        A button style to switch between 'solid', 'outline'.""")

    _rename: ClassVar[Mapping[str, str | None]] = {'name': 'label', 'button_style': None}

    _source_transforms: ClassVar[Mapping[str, str | None]] = {'button_style': None}

    _stylesheets: ClassVar[List[str]] = [f'{CDN_DIST}css/button.css']

    __abstract = True

    def _process_param_change(self, params):
        if 'button_style' in params or 'css_classes' in params:
            params['css_classes'] = [
                params.pop('button_style', self.button_style)
            ] + params.get('css_classes', self.css_classes)
        return super()._process_param_change(params)


class IconMixin(Widget):

    icon = param.String(default=None, doc="""
        An icon to render to the left of the button label. Either an SVG or an
        icon name which is loaded from https://tabler-icons.io.""")

    icon_size = param.String(default='1em', doc="""
        Size of the icon as a string, e.g. 12px or 1em.""")

    _rename: ClassVar[Mapping[str, str | None]] = {
        'icon_size': None, '_icon': 'icon', 'icon': None
    }

    __abstract = True

    def __init__(self, **params) -> None:
        self._rename = dict(self._rename, **IconMixin._rename)
        super().__init__(**params)

    def _process_param_change(self, params):
        icon_size = params.pop('icon_size', self.icon_size)
        if params.get('icon') is not None:
            icon = params['icon']
            if icon.lstrip().startswith('<svg'):
                icon_model = SVGIcon(svg=icon, size=icon_size)
            else:
                icon_model = TablerIcon(icon_name=icon, size=icon_size)
            params['_icon'] = icon_model
        return super()._process_param_change(params)


class _ClickButton(_ButtonBase, IconMixin):

    __abstract = True

    _event: ClassVar[str] = 'button_click'

    _source_transforms: ClassVar[Mapping[str, str | None]] = {
        'button_style': None,
    }

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
        model = super()._get_model(doc, root, parent, comm)
        self._register_events(self._event, model=model, doc=doc, comm=comm)
        return model

    def js_on_click(self, args: Dict[str, Any] = {}, code: str = "") -> Callback:
        """
        Allows defining a JS callback to be triggered when the button
        is clicked.

        Arguments
        ----------
        args: dict
          A mapping of objects to make available to the JS callback
        code: str
          The Javascript code to execute when the button is clicked.

        Returns
        -------
        callback: Callback
          The Callback which can be used to disable the callback.
        """
        from ..links import Callback
        return Callback(self, code={'event:'+self._event: code}, args=args)

    def jscallback(self, args: Dict[str, Any] = {}, **callbacks: str) -> Callback:
        """
        Allows defining a Javascript (JS) callback to be triggered when a property
        changes on the source object. The keyword arguments define the
        properties that trigger a callback and the JS code that gets
        executed.

        Arguments
        ----------
        args: dict
          A mapping of objects to make available to the JS callback
        **callbacks: dict
          A mapping between properties on the source model and the code
          to execute when that property changes

        Returns
        -------
        callback: Callback
          The Callback which can be used to disable the callback.
        """
        for k, v in list(callbacks.items()):
            if k == 'clicks':
                k = 'event:'+self._event
            val = self._rename.get(v, v)
            if val is not None:
                callbacks[k] = val
        return Callback(self, code=callbacks, args=args)


class Button(_ClickButton):
    """
    The `Button` widget allows triggering events when the button is
    clicked.

    The Button provides a `value` parameter, which will toggle from
    `False` to `True` while the click event is being processed

    It also provides an additional `clicks` parameter, that can be
    watched to subscribe to click events.

    Reference: https://panel.holoviz.org/reference/widgets/Button.html#widgets-gallery-button

    :Example:

    >>> pn.widgets.Button(name='Click me', icon='caret-right', button_type='primary')
    """

    clicks = param.Integer(default=0, doc="""
        Number of clicks (can be listened to)""")

    value = param.Event(doc="""
        Toggles from False to True while the event is being processed.""")

    _rename: ClassVar[Mapping[str, str | None]] = {
        'clicks': None, 'name': 'label', 'value': None
    }

    _target_transforms: ClassVar[Mapping[str, str | None]] = {
        'event:button_click': None, 'value': None
    }

    _widget_type: ClassVar[Type[Model]] = _BkButton

    def __init__(self, **params):
        click_handler = params.pop('on_click', None)
        super().__init__(**params)
        if click_handler:
            self.on_click(click_handler)

    @property
    def _linkable_params(self) -> List[str]:
        return super()._linkable_params + ['value']

    def jslink(
        self, target: JSLinkTarget, code: Optional[Dict[str, str]] = None,
        args: Optional[Dict[str, Any]] = None, bidirectional: bool = False,
        **links: str
    ) -> Link:
        """
        Links properties on the this Button to those on the
        `target` object in Javascript (JS) code.

        Supports two modes, either specify a
        mapping between the source and target model properties as
        keywords or provide a dictionary of JS code snippets which
        maps from the source parameter to a JS code snippet which is
        executed when the property changes.

        Arguments
        ----------
        target: panel.viewable.Viewable | bokeh.model.Model | holoviews.core.dimension.Dimensioned
          The target to link the value(s) to.
        code: dict
          Custom code which will be executed when the widget value
          changes.
        args: dict
          A mapping of objects to make available to the JS callback
        bidirectional: boolean
          Whether to link source and target bi-directionally. Default is `False`.
        **links: dict[str,str]
          A mapping between properties on the source model and the
          target model property to link it to.

        Returns
        -------
        Link
          The Link can be used unlink the widget and the target model.
        """
        links = {'event:'+self._event if p == 'value' else p: v for p, v in links.items()}
        return super().jslink(target, code, args, bidirectional, **links)

    def _process_event(self, event: param.parameterized.Event) -> None:
        self.param.trigger('value')
        self.clicks += 1

    def on_click(
        self, callback: Callable[[param.parameterized.Event], None]
    ) -> param.parameterized.Watcher:
        """
        Register a callback to be executed when the `Button` is clicked.

        The callback is given an `Event` argument declaring the number of clicks

        Arguments
        ---------
        callback: (Callable[[param.parameterized.Event], None])
            The function to run on click events. Must accept a positional `Event` argument

        Returns
        -------
        watcher: param.Parameterized.Watcher
          A `Watcher` that executes the callback when the button is clicked.
        """
        return self.param.watch(callback, 'clicks', onlychanged=False)


class Toggle(_ButtonBase, IconMixin):
    """The `Toggle` widget allows toggling a single condition between `True`/`False` states.

    This widget is interchangeable with the `Checkbox` widget.

    Reference: https://panel.holoviz.org/reference/widgets/Toggle.html

    :Example:

    >>> Toggle(name='Toggle', button_type='success')
    """

    value = param.Boolean(default=False, doc="""
        Whether the button is currently toggled.""")

    _rename: ClassVar[Mapping[str, str | None]] = {
        'value': 'active', 'name': 'label',
    }

    _supports_embed: ClassVar[bool] = True

    _widget_type: ClassVar[Type[Model]] = _BkToggle

    def _get_embed_state(self, root, values=None, max_opts=3):
        return (self, self._models[root.ref['id']][0], [False, True],
                lambda x: x.active, 'active', 'cb_obj.active')


class MenuButton(_ClickButton):
    """
    The `MenuButton` widget allows specifying a list of menu items to
    select from triggering events when the button is clicked.

    Unlike other widgets, it does not have a `value`
    parameter. Instead it has a `clicked` parameter that can be
    watched to trigger events and which reports the last clicked menu
    item.

    Reference: https://panel.holoviz.org/reference/widgets/MenuButton.html

    :Example:

    >>> menu_items = [('Option A', 'a'), ('Option B', 'b'), None, ('Option C', 'c')]
    >>> MenuButton(name='Dropdown', items=menu_items, button_type='primary')
    """

    clicked = param.String(default=None, doc="""
      Last menu item that was clicked.""")

    items = param.List(default=[], doc="""
      Menu items in the dropdown. Allows strings, tuples of the form
      (title, value) or Nones to separate groups of items.""")

    split = param.Boolean(default=False, doc="""
      Whether to add separate dropdown area to button.""")

    _event: ClassVar[str] = 'menu_item_click'

    _rename: ClassVar[Mapping[str, str | None]] = {'name': 'label', 'items': 'menu', 'clicked': None}

    _widget_type: ClassVar[Type[Model]] = _BkDropdown

    def __init__(self, **params):
        click_handler = params.pop('on_click', None)
        super().__init__(**params)
        if click_handler:
            self.on_click(click_handler)

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
        model = super()._get_model(doc, root, parent, comm)
        self._register_events('button_click', model=model, doc=doc, comm=comm)
        return model

    def _process_event(self, event):
        if isinstance(event, MenuItemClick):
            item = event.item
        elif isinstance(event, ButtonClick):
            item = self.name
        self.clicked = item

    def on_click(
        self, callback: Callable[[param.parameterized.Event], None]
    ) -> param.parameterized.Watcher:
        """
        Register a callback to be executed when the button is clicked.

        The callback is given an `Event` argument declaring the number of clicks

        Arguments
        ---------
        callback: (Callable[[param.parameterized.Event], None])
            The function to run on click events. Must accept a positional `Event` argument

        Returns
        -------
        watcher: param.Parameterized.Watcher
          A `Watcher` that executes the callback when the MenuButton is clicked.
        """
        return self.param.watch(callback, 'clicked', onlychanged=False)
