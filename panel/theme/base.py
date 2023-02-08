from __future__ import annotations

import functools
import os
import pathlib

from typing import TYPE_CHECKING

import param

from bokeh.models import ImportedStyleSheet
from bokeh.themes import Theme as _BkTheme, _dark_minimal

if TYPE_CHECKING:
    from bokeh.model import Model

    from ..viewable import Viewable


class Inherit:
    """
    Singleton object to declare stylesheet inheritance.
    """


class Theme(param.Parameterized):

    base_css = param.Filename()

    bokeh_theme = param.ClassSelector(class_=(_BkTheme, str), default=None)

    css = param.Filename()

    _modifiers = {}


BOKEH_DARK = dict(_dark_minimal.json)
BOKEH_DARK['attrs']['Plot'].update({
    "background_fill_color": "#2b3035",
    "border_fill_color": "#212529",
})


class DefaultTheme(Theme):

    base_css = param.Filename(default=pathlib.Path(__file__).parent / 'css' / 'default.css')

    _name = 'default'


class DarkTheme(Theme):

    base_css = param.Filename(default=pathlib.Path(__file__).parent / 'css' / 'dark.css')

    bokeh_theme = param.ClassSelector(class_=(_BkTheme, str),
                                      default=_BkTheme(json=BOKEH_DARK))

    _name = 'dark'


class Themer(param.Parameterized):

    theme = param.ClassSelector(class_=Theme)

    _modifiers = {}

    _resources = {}

    _themes = {
        'default': DefaultTheme,
        'dark': DarkTheme
    }

    def __init__(self, theme=None, **params):
        if isinstance(theme, type) and issubclass(theme, Theme):
            theme = theme._name
        theme = self._themes[theme]()
        super().__init__(theme=theme, **params)

    def apply(self, viewable, root: Model, isolated: bool=True):
        with root.document.models.freeze():
            self._reapply(viewable, root)
            if self.theme and self.theme.bokeh_theme and root.document:
                root.document.theme = self.theme.bokeh_theme

    def _reapply(self, viewable: Viewable, root: Model, isolated: bool=True) -> None:
        ref = root.ref['id']
        for o in viewable.select():
            self._apply_modifiers(o, ref, self.theme, isolated)

    def _apply_hooks(self, viewable: Viewable, root: Model) -> None:
        with root.document.models.freeze():
            self._reapply(viewable, root, isolated=False)

    @classmethod
    def _apply_modifiers(cls, viewable: Viewable, mref: str, theme: Theme, isolated: bool) -> None:
        if mref not in viewable._models:
            return
        model, _ = viewable._models[mref]
        modifiers, child_modifiers = cls._resolve_modifiers(type(viewable), theme)
        modifiers = dict(modifiers)
        if 'stylesheets' in modifiers:
            if isolated:
                pre = list(cls._resources.get('css', []))
                if theme.base_css:
                    base_css = theme.base_css
                    if os.path.isfile(base_css):
                        base_css = os.path.join('bundled', 'theme', os.path.basename(base_css))
                    pre.append(base_css)
            else:
                pre = []
            modifiers['stylesheets'] = [
                ImportedStyleSheet(url=sts) if sts.endswith('.css') else sts
                for sts in pre+modifiers['stylesheets']
            ]
        if child_modifiers:
            for child in viewable:
                cls._apply_params(child, mref, child_modifiers)
        if modifiers:
            cls._apply_params(viewable, mref, modifiers)

    @classmethod
    def _resolve_stylesheets(cls, value, defining_cls, inherited):
        new_value = []
        for v in value:
            if v is Inherit:
                new_value.extend(inherited)
            elif isinstance(v, str) and v.endswith('.css'):
                if v.startswith('http'):
                    url = v
                elif v.startswith('/'):
                    url = v[1:]
                else:
                    url = os.path.join('bundled', cls.__name__.lower(), v)
                new_value.append(url)
            else:
                new_value.append(v)
        return new_value

    @classmethod
    @functools.cache
    def _resolve_modifiers(cls, vtype, theme):
        """
        Iterate over the class hierarchy in reverse order and accumulate
        all modifiers that apply to the objects class and its super classes.
        """
        modifiers, child_modifiers = {}, {}
        for scls in vtype.__mro__[::-1]:
            cls_modifiers = cls._modifiers.get(scls, {})
            if cls_modifiers:
                # Find the Template class the options were first defined on
                def_cls = [
                    super_cls for super_cls in cls.__mro__[::-1]
                    if getattr(super_cls, '_modifiers', {}).get(scls) is cls_modifiers
                ][0]

                for prop, value in cls_modifiers.items():
                    if prop == 'children':
                        continue
                    elif prop == 'stylesheets':
                        modifiers[prop] = cls._resolve_stylesheets(value, def_cls, modifiers.get(prop, []))
                    else:
                        modifiers[prop] = value
            modifiers.update(theme._modifiers.get(scls, {}))
            child_modifiers.update(cls_modifiers.get('children', {}))
        return modifiers, child_modifiers

    @classmethod
    def _apply_params(cls, viewable, mref, modifiers):
        model, _ = viewable._models[mref]
        params = {
            k: v for k, v in modifiers.items() if k != 'children' and
            getattr(viewable, k) == viewable.param[k].default
        }
        if 'stylesheets' in modifiers:
            params['stylesheets'] = modifiers['stylesheets'] + viewable.stylesheets
        props = viewable._process_param_change(params)
        model.update(**props)


THEMES = {
    'default': DefaultTheme,
    'dark': DarkTheme
}
