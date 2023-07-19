from __future__ import annotations

import functools
import os
import pathlib

from typing import (
    TYPE_CHECKING, Any, ClassVar, Dict, List, Literal, Tuple, Type,
)

import param

from bokeh.models import ImportedStyleSheet
from bokeh.themes import Theme as _BkTheme, _dark_minimal, built_in_themes

from ..config import config
from ..io.resources import (
    ResourceComponent, component_resource_path, get_dist_path,
    resolve_custom_path,
)
from ..util import relative_to

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model

    from ..io.resources import ResourceTypes
    from ..viewable import Viewable


class Inherit:
    """
    Singleton object to declare stylesheet inheritance.
    """


class Theme(param.Parameterized):
    """
    Theme objects declare the styles to switch between different color
    modes. Each `Design` may declare any number of color themes.

    `modifiers`
       The modifiers override parameter values of Panel components.
    """

    base_css = param.Filename(doc="""
        A stylesheet declaring the base variables that define the color
        scheme. By default this is inherited from a base class.""")

    bokeh_theme = param.ClassSelector(class_=(_BkTheme, str), default=None, doc="""
        A Bokeh Theme class that declares properties to apply to Bokeh
        models. This is necessary to ensure that plots and other canvas
        based components are styled appropriately.""")

    css = param.Filename(doc="""
       A stylesheet that overrides variables specifically for the
       Theme subclass. In most cases, this is not necessary.""")

    modifiers: ClassVar[Dict[Viewable, Dict[str, Any]]] = {}


BOKEH_DARK = dict(_dark_minimal.json)
BOKEH_DARK['attrs']['Plot'].update({
    "background_fill_color": "#2b3035",
    "border_fill_color": "#212529",
})

THEME_CSS = pathlib.Path(__file__).parent / 'css'


class DefaultTheme(Theme):
    """
    Baseclass for default or light themes.
    """

    base_css = param.Filename(default=THEME_CSS / 'default.css')

    _name: ClassVar[str] = 'default'


class DarkTheme(Theme):
    """
    Baseclass for dark themes.
    """

    base_css = param.Filename(default=THEME_CSS / 'dark.css')

    bokeh_theme = param.ClassSelector(class_=(_BkTheme, str),
                                      default=_BkTheme(json=BOKEH_DARK))

    _name: ClassVar[str] = 'dark'


class Design(param.Parameterized, ResourceComponent):

    theme = param.ClassSelector(class_=Theme, constant=True)

    # Defines parameter overrides to apply to each model
    modifiers: ClassVar[Dict[Viewable, Dict[str, Any]]] = {}

    # Defines the resources required to render this theme
    _resources: ClassVar[Dict[str, Dict[str, str]]] = {}

    # Declares valid themes for this Design
    _themes: ClassVar[Dict[str, Type[Theme]]] = {
        'default': DefaultTheme,
        'dark': DarkTheme
    }

    def __init__(self, theme=None, **params):
        if isinstance(theme, type) and issubclass(theme, Theme):
            theme = theme._name
        elif theme is None:
            theme = 'default'
        theme = self._themes[theme]()
        super().__init__(theme=theme, **params)

    def _reapply(
        self, viewable: Viewable, root: Model, old_models: List[Model] = None,
        isolated: bool=True, cache=None, document=None
    ) -> None:
        ref = root.ref['id']
        for o in viewable.select():
            if o.design and not isolated:
                continue
            elif not o.design and not isolated:
                o._design = self

            if old_models and ref in o._models:
                if o._models[ref][0] in old_models:
                    continue
            self._apply_modifiers(o, ref, self.theme, isolated, cache, document)

    def _apply_hooks(self, viewable: Viewable, root: Model, changed: Viewable, old_models=None) -> None:
        from ..io.state import state
        if root.document in state._stylesheets:
            cache = state._stylesheets[root.document]
        else:
            state._stylesheets[root.document] = cache = {}
        with root.document.models.freeze():
            self._reapply(changed, root, old_models, isolated=False, cache=cache, document=root.document)

    def _wrapper(self, viewable):
        return viewable

    @classmethod
    def _resolve_stylesheets(cls, value, defining_cls, inherited):
        from ..io.resources import resolve_stylesheet
        stylesheets = []
        for stylesheet in value:
            if stylesheet is Inherit:
                stylesheets.extend(inherited)
                continue
            resolved = resolve_stylesheet(defining_cls, stylesheet, 'modifiers')
            stylesheets.append(resolved)
        return stylesheets

    @classmethod
    @functools.lru_cache
    def _resolve_modifiers(cls, vtype, theme):
        """
        Iterate over the class hierarchy in reverse order and accumulate
        all modifiers that apply to the objects class and its super classes.
        """
        modifiers, child_modifiers = {}, {}
        for scls in vtype.__mro__[::-1]:
            cls_modifiers = cls.modifiers.get(scls, {})
            modifiers.update(theme.modifiers.get(scls, {}))
            for super_cls in cls.__mro__[::-1]:
                cls_modifiers = getattr(super_cls, 'modifiers', {}).get(scls, {})
                for prop, value in cls_modifiers.items():
                    if prop == 'children':
                        continue
                    elif prop == 'stylesheets':
                        modifiers[prop] = cls._resolve_stylesheets(value, super_cls, modifiers.get(prop, []))
                    else:
                        modifiers[prop] = value
                child_modifiers.update(cls_modifiers.get('children', {}))
        return modifiers, child_modifiers

    @classmethod
    def _get_modifiers(
        cls, viewable: Viewable, theme: Theme = None, isolated: bool = True
    ):
        from ..io.resources import (
            CDN_DIST, component_resource_path, resolve_custom_path,
        )
        modifiers, child_modifiers = cls._resolve_modifiers(type(viewable), theme)
        modifiers = dict(modifiers)
        if 'stylesheets' in modifiers:
            if isolated:
                pre = list(cls._resources.get('css', {}).values())
                for p in ('base_css', 'css'):
                    css = getattr(theme, p)
                    if css is None:
                        continue
                    css = pathlib.Path(css)
                    if relative_to(css, THEME_CSS):
                        pre.append(f'{CDN_DIST}bundled/theme/{css.name}')
                    elif resolve_custom_path(theme, css):
                        pre.append(component_resource_path(theme, p, css))
                    else:
                        pre.append(css.read_text(encoding='utf-8'))
            else:
                pre = []
            modifiers['stylesheets'] = pre + modifiers['stylesheets']
        return modifiers, child_modifiers

    @classmethod
    def _patch_modifiers(cls, doc, modifiers, cache):
        if 'stylesheets' in modifiers:
            stylesheets = []
            for sts in modifiers['stylesheets']:
                if sts.endswith('.css'):
                    if cache and sts in cache:
                        sts = cache[sts]
                    else:
                        sts = ImportedStyleSheet(url=sts)
                        if cache is not None:
                            cache[sts.url] = sts
                stylesheets.append(sts)
            modifiers['stylesheets'] = stylesheets

    @classmethod
    def _apply_modifiers(
        cls, viewable: Viewable, mref: str, theme: Theme, isolated: bool,
        cache={}, document=None
    ) -> None:
        if mref not in viewable._models:
            return
        model, _ = viewable._models[mref]
        modifiers, child_modifiers = cls._get_modifiers(viewable, theme, isolated)
        cls._patch_modifiers(model.document or document, modifiers, cache)
        if child_modifiers:
            for child in viewable:
                cls._apply_params(child, mref, child_modifiers, document)
        if modifiers:
            cls._apply_params(viewable, mref, modifiers, document)

    @classmethod
    def _apply_params(cls, viewable, mref, modifiers, document=None):
        # Apply params never sync the modifier values with the Viewable
        # This should not be a concern since most `Layoutable` properties,
        # e.g. stylesheets or sizing_mode, are not synced between the
        # Panel component and the model anyway however in certain edge cases
        # this may end up causing issues.
        from ..io.resources import CDN_DIST, patch_stylesheet

        model, _ = viewable._models[mref]
        params = {
            k: v for k, v in modifiers.items() if k != 'children' and
            getattr(viewable, k) == viewable.param[k].default
        }
        if 'stylesheets' in modifiers:
            params['stylesheets'] = modifiers['stylesheets'] + viewable.stylesheets
        props = viewable._process_param_change(params)
        doc = model.document or document
        if doc and 'dist_url' in doc._template_variables:
            dist_url = doc._template_variables['dist_url']
        else:
            dist_url = CDN_DIST
        for stylesheet in props.get('stylesheets', []):
            if isinstance(stylesheet, ImportedStyleSheet):
                patch_stylesheet(stylesheet, dist_url)

        # Do not update stylesheets if they match
        if 'stylesheets' in props and len(model.stylesheets) == len(props['stylesheets']):
            all_match = True
            stylesheets = []
            for st1, st2 in zip(model.stylesheets, props['stylesheets']):
                if st1 == st2:
                    stylesheets.append(st1)
                    continue
                elif type(st1) is type(st2) and isinstance(st1, ImportedStyleSheet) and st1.url == st2.url:
                    stylesheets.append(st1)
                    continue
                stylesheets.append(st2)
                all_match = False
            if all_match:
                del props['stylesheets']
            else:
                props['stylesheets'] = stylesheets

        model.update(**props)
        if hasattr(viewable, '_synced_properties') and 'objects' in viewable._property_mapping:
            obj_key = viewable._property_mapping['objects']
            child_props = {
                p: v for p, v in params.items() if p in viewable._synced_properties
            }
            for child in getattr(model, obj_key):
                child.update(**child_props)

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def apply(self, viewable: Viewable, root: Model, isolated: bool=True):
        """
        Applies the Design to a Viewable and all it children.

        Arguments
        ---------
        viewable: Viewable
            The Viewable to apply the Design to.
        root: Model
            The root Bokeh model to apply the Design to.
        isolated: bool
            Whether the Design is applied to an individual component
            or embedded in a template that ensures the resources,
            such as CSS variable definitions and JS are already
            initialized.
        """
        doc = root.document
        if not doc:
            self._reapply(viewable, root, isolated=isolated)
            return

        from ..io.state import state
        if doc in state._stylesheets:
            cache = state._stylesheets[doc]
        else:
            state._stylesheets[doc] = cache = {}
        with doc.models.freeze():
            self._reapply(viewable, root, isolated=isolated, cache=cache)
            if self.theme and self.theme.bokeh_theme and doc:
                doc.theme = self.theme.bokeh_theme

    def apply_bokeh_theme_to_model(self, model: Model, theme_override=None):
        """
        Applies the Bokeh theme associated with this Design system
        to a model.

        Arguments
        ---------
        model: bokeh.model.Model
            The Model to apply the theme on.
        theme_override: str | None
            A different theme to apply.
        """
        theme = theme_override or self.theme.bokeh_theme
        if isinstance(theme, str):
            theme = built_in_themes.get(theme)
        if not theme:
            return
        for sm in model.references():
            theme.apply_to_model(sm)

    def resolve_resources(
        self, cdn: bool | Literal['auto'] = 'auto', include_theme: bool = True
    ) -> ResourceTypes:
        """
        Resolves the resources required for this design component.

        Arguments
        ---------
        cdn: bool | Literal['auto']
            Whether to load resources from CDN or local server. If set
            to 'auto' value will be automatically determine based on
            global settings.
        include_theme: bool
            Whether to include theme resources.

        Returns
        -------
        Dictionary containing JS and CSS resources.
        """
        resource_types = super().resolve_resources(cdn)
        if not include_theme:
            return resource_types
        dist_path = get_dist_path(cdn=cdn)
        css_files = resource_types['css']
        theme = self.theme
        for attr in ('base_css', 'css'):
            css = getattr(theme, attr, None)
            if css is None:
                continue
            basename = os.path.basename(css)
            key = 'theme_base' if 'base' in attr else 'theme'
            if relative_to(css, THEME_CSS):
                css_files[key] = dist_path + f'bundled/theme/{basename}'
            elif resolve_custom_path(theme, css):
                owner = type(theme).param[attr].owner
                css_files[key] = component_resource_path(owner, attr, css)
        return resource_types

    def params(
        self, viewable: Viewable, doc: Document | None = None
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Provides parameter values to apply the provided Viewable.

        Arguments
        ---------
        viewable: Viewable
            The Viewable to return modifiers for.
        doc: Document | None
            Document the Viewable will be rendered into. Useful
            for caching any stylesheets that are created.

        Returns
        -------
        modifiers: Dict[str, Any]
            Dictionary of parameter values to apply to the Viewable.
        child_modifiers: Dict[str, Any]
            Dictionary of parameter values to apply to the children
            of the Viewable.
        """
        from ..io.state import state
        if doc is None:
            cache = {}
        elif doc in state._stylesheets:
            cache = state._stylesheets[doc]
        else:
            state._stylesheets[doc] = cache = {}
        modifiers, child_modifiers = self._get_modifiers(viewable, theme=self.theme)
        self._patch_modifiers(doc, modifiers, cache)
        return modifiers, child_modifiers


config.param.design.class_ = Design
THEMES = {
    'default': DefaultTheme,
    'dark': DarkTheme
}
