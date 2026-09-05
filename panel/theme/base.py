from __future__ import annotations

import base64
import functools
import importlib
import os
import pathlib
import typing as t

import param

from bokeh.models import ImportedStyleSheet
from bokeh.themes import Theme as _BkTheme, _dark_minimal, built_in_themes

from ..config import config
from ..custom import PyComponent
from ..io.resources import (
    CDN_DIST, DIST_DIR, JS_VERSION, ResourceComponent, component_resource_path,
    get_dist_path, resolve_custom_path,
)
from ..io.state import set_curdoc, state
from ..util import _descendents, relative_to

if t.TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model

    from ..io.resources import ResourceTypes
    from ..viewable import Viewable

T = t.TypeVar('T', bound=type)


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

    modifiers: t.ClassVar[dict[type[Viewable], dict[str, t.Any]]] = {}


BOKEH_DARK = dict(_dark_minimal.json)
BOKEH_DARK['attrs']['Plot'].update({
    "background_fill_color": "#2b3035",
    "border_fill_color": "#212529",
})

THEME_CSS = pathlib.Path(__file__).parent / 'css'

# Maps the config parameters that control the loading indicator to the
# keys of the options dictionary a Design declares them with.
_LOADING_CONFIG = {
    'loading_spinner': 'spinner',
    'loading_color': 'color',
    'loading_max_height': 'max_height'
}


class DefaultTheme(Theme):
    """
    Baseclass for default or light themes.
    """

    base_css = param.Filename(default=THEME_CSS / 'default.css')

    _name: t.ClassVar[str] = 'default'


class DarkTheme(Theme):
    """
    Baseclass for dark themes.
    """

    base_css = param.Filename(default=THEME_CSS / 'dark.css')

    bokeh_theme = param.ClassSelector(class_=(_BkTheme, str),
                                      default=_BkTheme(json=BOKEH_DARK))

    _name: t.ClassVar[str] = 'dark'


def _stylesheet_cache(doc: Document) -> dict[str, ImportedStyleSheet]:
    """
    Returns the ImportedStyleSheet cache scoped to a particular Document.

    Stylesheets must never be shared between Documents since Bokeh
    destroys all models on a Document once the session ends, leaving the
    stylesheets it holds without a url.
    """
    if doc not in state._stylesheets:
        state._stylesheets[doc] = {}
    return state._stylesheets[doc]


class Design(param.Parameterized, ResourceComponent):

    theme = param.ClassSelector(class_=Theme, constant=True)

    # Defines parameter overrides to apply to each model
    modifiers: t.ClassVar[dict[type[Viewable], dict[str, t.Any]]] = {}

    # Maps a component type to the equivalent component in this design
    # system, e.g. to substitute a Material UI widget for a classic one
    # when a widget is generated on the user's behalf.
    component_mapping: t.ClassVar[dict[type, type]] = {}

    # Maps a Parameter type to the widget type to generate for it, or to
    # a callable which is given the Parameter and returns a widget type.
    # Takes precedence over the component_mapping since a design system
    # may split or merge the classic mapping, e.g. by resolving separate
    # widgets for dict, list and tuple parameters.
    widget_mapping: t.ClassVar[dict[type[param.Parameter], type | t.Callable[[param.Parameter], type | None]]] = {}

    # Defines the resources required to render this theme
    _resources = {}

    # Overrides the loading indicator defaults, i.e. the spinner, color
    # and max_height config values. Explicit user settings always win.
    _loading_options: t.ClassVar[dict[str, t.Any]] = {}

    # Declares valid themes for this Design
    _themes: t.ClassVar[dict[str, type[Theme]]] = {
        'default': DefaultTheme,
        'dark': DarkTheme
    }

    _cache: t.ClassVar[dict[str, ImportedStyleSheet]] = {}

    def __init__(self, theme=None, **params):
        if isinstance(theme, type) and issubclass(theme, Theme):
            theme = theme._name
        elif theme is None:
            theme = 'default'
        theme = self._themes[theme]()
        super().__init__(theme=theme, **params)

    def _reapply(
        self, viewable: Viewable, root: Model, old_models: list[Model] | None = None,
        isolated: bool = True, cache=None, document: Document | None = None
    ) -> None:
        ref = root.ref['id']
        seen = set()
        for o in viewable.select():
            if o.design and not isolated:
                continue
            elif not o.design and not isolated:
                o._design = self

            if ref in o._models:
                model = o._models[ref][0]
                if (old_models and model in old_models) or model in seen:
                    continue
                seen.add(model)
            theme = self.theme
            if theme is None:
                continue
            if document:
                # Theme hook may be applied during callback triggered from a different document
                # we must set_curdoc to ensure style caches are not shared across documents
                with set_curdoc(document):
                    self._apply_modifiers(o, ref, theme, isolated, cache, document)
            else:
                self._apply_modifiers(o, ref, theme, isolated, cache, document)

    def _apply_hooks(self, viewable: Viewable, root: Model, changed: Viewable, old_models=None) -> None:
        cache: dict[str, ImportedStyleSheet] = {} if root.document is None else _stylesheet_cache(root.document)
        if root.document:
            with root.document.models.freeze():
                self._reapply(changed, root, old_models, isolated=False, cache=cache, document=root.document)
        else:
            self._reapply(changed, root, old_models, isolated=False, cache=cache)

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
            if resolved not in stylesheets:
                stylesheets.append(resolved)
        return stylesheets

    @classmethod
    @functools.lru_cache
    def _resolve_modifiers(cls, vtype, theme, is_server=False):
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
        cls, viewable: Viewable, theme: Theme | None = None, isolated: bool = True
    ):
        from ..io.resources import (
            CDN_DIST, component_resource_path, resolve_custom_path,
        )
        theme_type = type(theme) if isinstance(theme, Theme) else theme
        is_server = bool(state.curdoc.session_context) if not state._is_pyodide and state.curdoc else False
        modifiers, child_modifiers = cls._resolve_modifiers(type(viewable), theme_type, is_server=is_server)  # type: ignore
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
    def _patch_modifiers(cls, doc: Document | None, modifiers: dict[str, t.Any], cache: dict[str, ImportedStyleSheet]):
        from ..io.resources import stylesheet_url
        if 'stylesheets' in modifiers:
            stylesheets = []
            for sts in modifiers['stylesheets']:
                if sts.endswith('.css'):
                    cached = cache.get(sts) if cache else None
                    # A cached stylesheet that lost its url was destroyed
                    # along with the Document it was rendered into and
                    # has to be recreated.
                    if cached is None or stylesheet_url(cached) is None:
                        cached = ImportedStyleSheet(url=sts)
                        if cache is not None:
                            cache[sts] = cached
                    sts = cached
                stylesheets.append(sts)
            modifiers['stylesheets'] = stylesheets

    @classmethod
    def _apply_modifiers(
        cls, viewable: Viewable, mref: str, theme: Theme, isolated: bool,
        cache=None, document=None
    ) -> None:
        if mref not in viewable._models:
            return
        model, _ = viewable._models[mref]
        doc = model.document or document
        if cache is None:
            cache = cls._cache if doc is None else _stylesheet_cache(doc)
        modifiers, child_modifiers = cls._get_modifiers(viewable, theme, isolated)
        cls._patch_modifiers(doc, modifiers, cache)
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
        from ..io.resources import CDN_DIST, patch_stylesheet, stylesheet_url

        if mref not in viewable._models:
            return
        model, _ = viewable._models[mref]
        params = {
            k: v for k, v in modifiers.items() if k != 'children' and
            getattr(viewable, k) == viewable.param[k].default
        }
        if 'stylesheets' in modifiers:
            params['stylesheets'] = modifiers['stylesheets'] + viewable.stylesheets

        if isinstance(viewable, PyComponent):
            props = viewable._view__._process_param_change(params)
        else:
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
                elif type(st1) is type(st2) and isinstance(st1, ImportedStyleSheet):
                    url1 = stylesheet_url(st1)
                    if url1 is not None and url1 == stylesheet_url(st2):
                        stylesheets.append(st1)
                        continue
                stylesheets.append(st2)
                all_match = False
            if all_match:
                del props['stylesheets']
            else:
                props['stylesheets'] = stylesheets
        if props:
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

    @classmethod
    def resolve_component(cls, component: T) -> T:
        """
        Resolves the component to render in place of the provided
        component type.

        Only exact matches in the `component_mapping` are substituted,
        since a subclass may declare behavior the design system's
        equivalent does not implement.

        Parameters
        ----------
        component: type
            The component type to find the equivalent for.

        Returns
        -------
        The equivalent component in this design system, or the component
        itself if the design system does not declare one.
        """
        return t.cast('T', cls.component_mapping.get(component, component))

    @classmethod
    def loading_options(cls) -> dict[str, t.Any]:
        """
        Resolves the options that control the appearance of the loading
        indicator.

        The design system's `_loading_options` provide the defaults, any
        value the user set explicitly takes precedence.

        Returns
        -------
        Dictionary containing the spinner, color and max_height.
        """
        options = dict(cls._loading_options)
        for cname, name in _LOADING_CONFIG.items():
            value = getattr(config, cname)
            if name not in options or value != config.param[cname].default:
                options[name] = value
        return options

    @classmethod
    def loading_css_classes(cls) -> list[str]:
        """
        Returns the CSS classes that mark a component as loading.
        """
        from ..io.loading import LOADING_INDICATOR_CSS_CLASS
        return [LOADING_INDICATOR_CSS_CLASS, f'pn-{cls.loading_options()["spinner"]}']

    @classmethod
    def loading_css(cls) -> str:
        """
        Returns the CSS that styles the loading indicator.
        """
        from ..io.resources import loading_css
        options = cls.loading_options()
        return loading_css(
            options['spinner'], options['color'], options['max_height']
        )

    @classmethod
    def loading_resources(
        cls, inline: bool = False, include_base: bool = True,
        dist_path: str | None = None
    ) -> dict[str, list[str]]:
        """
        Returns the resources required to render the loading indicator,
        e.g. when saving or converting an application.

        Parameters
        ----------
        inline: bool
            Whether to inline the stylesheets instead of linking them.
        include_base: bool
            Whether to include the base loading stylesheet. May be
            disabled if the output already loads it, e.g. because it is
            rendered into a Panel template.
        dist_path: str | None
            The path the Panel distribution is served from. If not
            declared the CDN is used and, when inlining, assets are
            embedded in the stylesheet.

        Returns
        -------
        Dictionary containing stylesheet URLs and raw CSS.
        """
        options = cls.loading_options()
        css: list[str] = []
        raw_css: list[str] = []
        if include_base:
            if inline:
                raw_css.append(cls._inline_loading_css(options, dist_path))
            else:
                css.append(f'{dist_path or CDN_DIST}css/loading.css')
        raw_css.append(cls.loading_css())
        return {'css': css, 'raw_css': raw_css}

    @classmethod
    def _inline_loading_css(cls, options: dict[str, t.Any], dist_path: str | None) -> str:
        base = (DIST_DIR / 'css' / 'loading.css').read_text(encoding='utf-8')
        if dist_path is not None:
            return base.replace('../assets', f'{dist_path}assets')
        svg_name = f'{options["spinner"]}_spinner.svg'
        svg_path = DIST_DIR / 'assets' / svg_name
        if not svg_path.is_file():
            return base
        b64 = base64.b64encode(svg_path.read_bytes()).decode('utf-8')
        return base.replace(
            f'../assets/{svg_name}', f'data:image/svg+xml;base64,{b64}'
        )

    @classmethod
    def resolve_widget(cls, parameter: param.Parameter) -> type[t.Any] | None:
        """
        Resolves the widget type to generate for a Parameter.

        Parameters
        ----------
        parameter: param.Parameter
            The Parameter to resolve a widget for.

        Returns
        -------
        The widget type to render the Parameter with, or None if the
        design system does not override the default resolution.
        """
        if not cls.widget_mapping:
            return None
        for ptype in type(parameter).__mro__:
            if ptype not in cls.widget_mapping:
                continue
            wtype = cls.widget_mapping[ptype]
            if not isinstance(wtype, type) and callable(wtype):
                resolved = wtype(parameter)
                if resolved is None:
                    continue
                return resolved
            return wtype
        return None

    def apply(self, viewable: Viewable, root: Model, isolated: bool = True):
        """
        Applies the Design to a Viewable and all it children.

        Parameters
        ----------
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

        cache = _stylesheet_cache(doc)
        with doc.models.freeze():
            self._reapply(viewable, root, isolated=isolated, cache=cache)
            if self.theme and self.theme.bokeh_theme and doc:
                doc.theme = self.theme.bokeh_theme

    def apply_bokeh_theme_to_model(self, model: Model, theme_override=None):
        """
        Applies the Bokeh theme associated with this Design system
        to a model.

        Parameters
        ----------
        model: bokeh.model.Model
            The Model to apply the theme on.
        theme_override: str | None
            A different theme to apply.
        """
        default_theme = self.theme.bokeh_theme if self.theme is not None else None
        theme = theme_override or default_theme
        if isinstance(theme, str):
            # theme is an arbitrary string, not necessarily one of the
            # built-in theme name literals.
            theme = built_in_themes.get(theme)  # type: ignore[call-overload]
        if not theme:
            return
        for sm in model.references():
            theme.apply_to_model(sm)

    def resolve_resources(
        self,
        cdn: bool | t.Literal['auto'] = 'auto',
        extras: dict[str, dict[str, str]] | None = None,
        include_theme: bool = True
    ) -> ResourceTypes:
        """
        Resolves the resources required for this design component.

        Parameters
        ----------
        cdn: bool | Literal['auto']
            Whether to load resources from CDN or local server. If set
            to 'auto' value will be automatically determine based on
            global settings.
        extras: dict[str, dict[str, str]] | None
            Additional resources to add to the bundle. Valid resource
            types include js, js_modules and css.
        include_theme: bool
            Whether to include theme resources.

        Returns
        -------
        Dictionary containing JS and CSS resources.
        """
        resource_types = super().resolve_resources(cdn=cdn, extras=extras)
        if not include_theme:
            return resource_types
        dist_path = get_dist_path(cdn=cdn)
        version_suffix = f'?v={JS_VERSION}'
        css_files = resource_types['css']
        theme = self.theme
        if theme is None:
            return resource_types
        for attr in ('base_css', 'css'):
            css = getattr(theme, attr, None)
            if css is None:
                continue
            basename = os.path.basename(css)
            key = 'theme_base' if 'base' in attr else 'theme'
            if relative_to(css, THEME_CSS):
                css_files[key] = dist_path + f'bundled/theme/{basename}{version_suffix}'
            elif resolve_custom_path(theme, css):
                owner = type(theme).param[attr].owner
                css_files[key] = component_resource_path(owner, attr, css)
        return resource_types

    def params(
        self, viewable: Viewable, doc: Document | None = None
    ) -> tuple[dict[str, t.Any], dict[str, t.Any]]:
        """
        Provides parameter values to apply the provided Viewable.

        Parameters
        ----------
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
        cache: dict[str, ImportedStyleSheet] = {} if doc is None else _stylesheet_cache(doc)
        modifiers, child_modifiers = self._get_modifiers(viewable, theme=self.theme)
        self._patch_modifiers(doc, modifiers, cache)
        return modifiers, child_modifiers


config.param.design.class_ = Design
THEMES = {
    'default': DefaultTheme,
    'dark': DarkTheme
}

# Maps a design name to the Design class implementing it, declared as a
# 'module.path.ClassName' or 'module.path:ClassName' reference. Allows
# design systems that do not live in panel.theme, and designs whose class
# name does not match the name they are referenced by, to be resolved,
# e.g. in pn.extension(design=...).
DESIGN_ALIASES: dict[str, str] = {
    'material-ui': 'panel.ui.theme.MaterialUIDesign',
}


def resolve_design(design: str | type[Design]) -> type[Design]:
    """
    Resolves the Design class given its name.

    Parameters
    ----------
    design: str | type[Design]
        The name of the Design or the Design itself.

    Returns
    -------
    The resolved Design class.
    """
    if not isinstance(design, str):
        return design
    name = design.lower()
    if name in DESIGN_ALIASES:
        return _resolve_design_alias(name, DESIGN_ALIASES[name])
    try:
        importlib.import_module(f'panel.theme.{name}')
    except ImportError:
        pass
    designs = {t.__name__.lower(): t for t in _descendents(Design, concrete=True)}
    if name not in designs:
        available = sorted(set(designs) | set(DESIGN_ALIASES))
        raise ValueError(
            f'Design {design!r} was not recognized, available design '
            f'systems include: {available}.'
        )
    return designs[name]


def _resolve_design_alias(name: str, ref: str) -> type[Design]:
    modname, _, clsname = ref.rpartition(':') if ':' in ref else ref.rpartition('.')
    try:
        module = importlib.import_module(modname)
    except ImportError as e:
        raise ValueError(
            f'Design {name!r} could not be resolved, importing {modname!r} '
            f'failed with: {e}'
        ) from e
    resolved = getattr(module, clsname, None)
    if not (isinstance(resolved, type) and issubclass(resolved, Design)):
        raise ValueError(
            f'Design {name!r} could not be resolved, {ref!r} does not '
            'reference a Design class.'
        )
    return resolved


def resolve_component(component: T) -> T:
    """
    Resolves the component to render in place of the provided component
    type given the currently active design system.

    Parameters
    ----------
    component: type
        The component type to find the equivalent for.

    Returns
    -------
    The equivalent component in the active design system, or the
    component itself if there is none.
    """
    design = config.design
    if design is None:
        return component
    return design.resolve_component(component)


def resolve_widget(parameter: param.Parameter) -> type[Viewable] | None:
    """
    Resolves the widget type to generate for a Parameter given the
    currently active design system.

    Parameters
    ----------
    parameter: param.Parameter
        The Parameter to resolve a widget for.

    Returns
    -------
    The widget type declared by the active design system, or None if it
    does not override the default resolution.
    """
    design = config.design
    if design is None:
        return None
    return design.resolve_widget(parameter)
