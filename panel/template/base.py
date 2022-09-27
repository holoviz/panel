"""
Templates allow multiple Panel objects to be embedded into custom HTML
documents.
"""
from __future__ import annotations

import os
import sys
import uuid

from functools import partial
from pathlib import Path, PurePath
from typing import (
    IO, TYPE_CHECKING, Any, ClassVar, Dict, List, Optional, Tuple, Type,
)

import param

from bokeh.document.document import Document
from bokeh.settings import settings as _settings
from pyviz_comms import JupyterCommManager as _JupyterCommManager

from ..config import _base_config, config, panel_extension
from ..io.model import add_to_doc
from ..io.notebook import render_template
from ..io.notifications import NotificationArea
from ..io.resources import (
    BUNDLE_DIR, CDN_DIST, CSS_URLS, DOC_DIST, JS_URLS, LOCAL_DIST, _env,
    component_resource_path, resolve_custom_path,
)
from ..io.save import save
from ..io.state import curdoc_locked, state
from ..layout import Column, GridSpec, ListLike
from ..models.comm_manager import CommManager
from ..pane import (
    HTML, HoloViews, Str, panel as _panel,
)
from ..pane.image import ImageBase
from ..reactive import ReactiveHTML
from ..util import isurl, url_path
from ..viewable import Renderable, ServableMixin, Viewable
from ..widgets import Button
from ..widgets.indicators import BooleanIndicator, LoadingSpinner
from .theme import THEMES, DefaultTheme, Theme

if TYPE_CHECKING:
    from bokeh.model import Model
    from bokeh.server.contexts import BokehSessionContext
    from jinja2 import Template as _Template
    from pyviz_comms import Comm
    from typing_extensions import Literal, TypedDict

    from ..io.location import Location

    class ResourcesType(TypedDict):
        css: Dict[str, str]
        js:  Dict[str, str]
        js_modules: Dict[str, str]
        extra_css: List[str]
        raw_css: List[str]


_server_info: str = (
    '<b>Running server:</b> <a target="_blank" href="https://localhost:{port}">'
    'https://localhost:{port}</a>'
)

FAVICON_URL: str = "/static/extensions/panel/images/favicon.ico"


class BaseTemplate(param.Parameterized, ServableMixin):

    location = param.Boolean(default=False, doc="""
        Whether to add a Location component to this Template.
        Note if this is set to true, the Jinja2 template must
        either insert all available roots or explicitly embed
        the location root with : {{ embed(roots.location) }}.""")

    # Dictionary of property overrides by Viewable type
    _modifiers: ClassVar[Dict[Type[Viewable], Dict[str, Any]]] = {}

    __abstract = True

    def __init__(
        self, template: str | _Template, items=None,
        nb_template: Optional[str | _Template] = None, **params
    ):
        super().__init__(**params)
        if isinstance(template, str):
            self._code: str | None = template
            self.template = _env.from_string(template)
        else:
            self._code = None
            self.template = template
        if isinstance(nb_template, str):
            self.nb_template = _env.from_string(nb_template)
        else:
            self.nb_template = nb_template or self.template
        self._render_items: Dict[str, Tuple[Renderable, List[str]]]  = {}
        self._render_variables: Dict[str, Any] = {}
        self._documents: List[Document] = []
        self._server = None
        self._layout = self._build_layout()

    def _build_layout(self) -> Column:
        str_repr = Str(repr(self))
        server_info = HTML('')
        button = Button(name='Launch server')
        def launch(event):
            if self._server:
                button.name = 'Launch server'
                server_info.object = ''
                self._server.stop()
                self._server = None
            else:
                button.name = 'Stop server'
                self._server = self._get_server(start=True, show=True)
                server_info.object = _server_info.format(port=self._server.port)
        button.param.watch(launch, 'clicks')
        return Column(str_repr, server_info, button)

    def __repr__(self) -> str:
        spacer = '\n    '
        objs = spacer.join([
            f'[{name}] {obj.__repr__(1)}'  # type: ignore
            for name, (obj, _) in self._render_items.items()
            if not name.startswith('_')
        ])
        return f'{type(self).__name__}{spacer}{objs}'

    def _apply_hooks(self, viewable: Viewable, root: Model) -> None:
        ref = root.ref['id']
        for o in viewable.select():
            self._apply_modifiers(o, ref)

    @classmethod
    def _apply_modifiers(cls, viewable: Viewable, mref: str) -> None:
        if mref not in viewable._models:
            return
        model, _ = viewable._models[mref]
        modifiers = cls._modifiers.get(type(viewable), {})
        child_modifiers = modifiers.get('children', {})
        if child_modifiers:
            for child in viewable:
                child_params = {
                    k: v for k, v in child_modifiers.items()
                    if getattr(child, k) == child.param[k].default
                }
                child.param.set_param(**child_params)
                child_props = child._process_param_change(child_params)
                child._models[mref][0].update(**child_props)
        params = {
            k: v for k, v in modifiers.items() if k != 'children' and
            getattr(viewable, k) == viewable.param[k].default
        }
        viewable.param.update(**params)
        props = viewable._process_param_change(params)
        model.update(**props)

    def _apply_root(self, name: str, model: Model, tags: List[str]) -> None:
        pass

    def _server_destroy(self, session_context: BokehSessionContext):
        doc = session_context._document
        if doc in state._templates:
            del state._templates[doc]
        self._documents.remove(doc)

    def _init_doc(
        self, doc: Optional[Document] = None, comm: Optional[Comm] = None,
        title: Optional[str] = None, notebook: bool = False,
        location: bool | Location=True
    ):
        document: Document = doc or curdoc_locked()
        self._documents.append(document)
        if document not in state._templates:
            state._templates[document] = self
        if location and self.location:
            self._add_location(document, location)
        document.on_session_destroyed(state._destroy_session) # type: ignore
        document.on_session_destroyed(self._server_destroy) # type: ignore

        if title or document.title == 'Bokeh Application':
            title = title or 'Panel Application'
            document.title = title

        # Initialize fake root. This is needed to ensure preprocessors
        # which assume that all models are owned by a single root can
        # link objects across multiple roots in a template.
        col = Column()
        preprocess_root = col.get_root(document, comm)
        col._hooks.append(self._apply_hooks)
        ref = preprocess_root.ref['id']
        objs, models = [], []

        for name, (obj, tags) in self._render_items.items():
            if self._apply_hooks not in obj._hooks:
                obj._hooks.append(self._apply_hooks)
            # We skip preprocessing on the individual roots
            model = obj.get_root(document, comm, preprocess=False)
            mref = model.ref['id']
            document.on_session_destroyed(obj._server_destroy) # type: ignore
            for sub in obj.select(Viewable):
                submodel = sub._models.get(mref)
                if submodel is None:
                    continue
                sub._models[ref] = submodel
                if isinstance(sub, HoloViews) and mref in sub._plots:
                    sub._plots[ref] = sub._plots.get(mref)
            obj._documents[document] = model
            model.name = name
            model.tags = tags
            self._apply_root(name, model, tags)
            add_to_doc(model, document, hold=bool(comm))
            objs.append(obj)
            models.append(model)

        # Here we ensure that the preprocessor is run across all roots
        # and set up session cleanup hooks for the fake root.
        state._fake_roots.append(ref) # Ensure no update is run
        state._views[ref] = (col, preprocess_root, document, comm)
        col.objects = objs
        preprocess_root.children[:] = models
        col._preprocess(preprocess_root)
        col._documents[document] = preprocess_root
        document.on_session_destroyed(col._server_destroy) # type: ignore

        if notebook:
            document.template = self.nb_template
        else:
            document.template = self.template
        document._template_variables.update(self._render_variables)
        return document

    def _repr_mimebundle_(
        self, include=None, exclude=None
    ) -> Tuple[Dict[str, str], Dict[str, Dict[str, str]]] | None:
        loaded = panel_extension._loaded
        if not loaded and 'holoviews' in sys.modules:
            import holoviews as hv
            loaded = hv.extension._loaded
        if not loaded:
            param.main.param.warning(
                'Displaying Panel objects in the notebook requires '
                'the panel extension to be loaded. Ensure you run '
                'pn.extension() before displaying objects in the '
                'notebook.'
            )
            return None

        try:
            assert get_ipython().kernel is not None # type: ignore # noqa
            state._comm_manager = _JupyterCommManager
        except Exception:
            pass

        from IPython.display import display

        doc = Document()
        comm = state._comm_manager.get_server_comm()
        self._init_doc(doc, comm, notebook=True)
        ref = doc.roots[0].ref['id']
        manager = CommManager(
            comm_id=comm.id, plot_id=ref, name='comm_manager'
        )
        client_comm = state._comm_manager.get_client_comm(
            on_msg=partial(self._on_msg, ref, manager),
            on_error=partial(self._on_error, ref),
            on_stdout=partial(self._on_stdout, ref)
        )
        manager.client_comm_id = client_comm.id
        doc.add_root(manager)

        if config.console_output != 'disable':
            handle = display(display_id=uuid.uuid4().hex)
            state._handles[ref] = (handle, [])

        return render_template(doc, comm, manager)

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def save(
        self, filename: str | os.PathLike | IO, title: Optional[str] = None,
        resources=None, embed: bool = False, max_states: int = 1000,
        max_opts: int = 3, embed_json: bool = False, json_prefix: str='',
        save_path: str='./', load_path: Optional[str] = None
    ) -> None:
        """
        Saves Panel objects to file.

        Arguments
        ---------
        filename: string or file-like object
           Filename to save the plot to
        title: string
           Optional title for the plot
        resources: bokeh resources
           One of the valid bokeh.resources (e.g. CDN or INLINE)
        embed: bool
           Whether the state space should be embedded in the saved file.
        max_states: int
           The maximum number of states to embed
        max_opts: int
           The maximum number of states for a single widget
        embed_json: boolean (default=True)
           Whether to export the data to json files
        json_prefix: str (default='')
           Prefix for the auto-generated json directory
        save_path: str (default='./')
           The path to save json files to
        load_path: str (default=None)
           The path or URL the json files will be loaded from.
        """
        if embed:
            raise ValueError("Embedding is not yet supported on Template.")

        return save(
            self, filename, title, resources, self.template,
            self._render_variables, embed, max_states, max_opts,
            embed_json, json_prefix, save_path, load_path
        )

    def server_doc(
        self, doc: Optional[Document] = None, title: str = None,
        location: bool | Location = True
    ) -> Document:
        """
        Returns a servable bokeh Document with the panel attached

        Arguments
        ---------
        doc : bokeh.Document (optional)
          The Bokeh Document to attach the panel to as a root,
          defaults to bokeh.io.curdoc()
        title : str
          A string title to give the Document
        location : boolean or panel.io.location.Location
          Whether to create a Location component to observe and
          set the URL location.

        Returns
        -------
        doc : bokeh.Document
          The Bokeh document the panel was attached to
        """
        return self._init_doc(doc, title=title, location=location)

    def select(self, selector=None):
        """
        Iterates over the Template and any potential children in the
        applying the Selector.

        Arguments
        ---------
        selector: type or callable or None
          The selector allows selecting a subset of Viewables by
          declaring a type or callable function to filter by.

        Returns
        -------
        viewables: list(Viewable)
        """
        objects = []
        for obj, _ in self._render_items.values():
            objects += obj.select(selector)
        return objects



class TemplateActions(ReactiveHTML):
    """
    A component added to templates that allows triggering events such
    as opening and closing a modal.
    """

    open_modal = param.Integer(default=0)

    close_modal = param.Integer(default=0)

    margin = param.Integer(default=0)

    _template: ClassVar[str] = ""

    _scripts: ClassVar[Dict[str, List[str] | str]] = {
        'open_modal': ["document.getElementById('pn-Modal').style.display = 'block'"],
        'close_modal': ["document.getElementById('pn-Modal').style.display = 'none'"],
    }


class BasicTemplate(BaseTemplate):
    """
    BasicTemplate provides a baseclass for templates with a basic
    organization including a header, sidebar and main area. Unlike the
    more generic Template class these default templates make it easy
    for a user to generate an application with a polished look and
    feel without having to write any Jinja2 template themselves.
    """

    config = param.ClassSelector(default=_base_config(), class_=_base_config,
                                 constant=True, doc="""
        Configuration object declaring custom CSS and JS files to load
        specifically for this template.""")

    busy_indicator = param.ClassSelector(default=LoadingSpinner(width=20, height=20),
                                         class_=BooleanIndicator, constant=True,
                                         allow_None=True, doc="""
        Visual indicator of application busy state.""")

    header = param.ClassSelector(class_=ListLike, constant=True, doc="""
        A list-like container which populates the header bar.""")

    main = param.ClassSelector(class_=ListLike, constant=True, doc="""
        A list-like container which populates the main area.""")

    main_max_width = param.String(default="", doc="""
        The maximum width of the main area. For example '800px' or '80%'.
        If the string is '' (default) no max width is set.""")

    sidebar = param.ClassSelector(class_=ListLike, constant=True, doc="""
        A list-like container which populates the sidebar.""")

    sidebar_width = param.Integer(330, doc="""
        The width of the sidebar in pixels. Default is 330.""")

    modal = param.ClassSelector(class_=ListLike, constant=True, doc="""
        A list-like container which populates the modal""")

    notifications = param.ClassSelector(class_=NotificationArea, constant=True, doc="""
        The NotificationArea instance attached to this template.
        Automatically added if config.notifications is set, but may
        also be provided explicitly.""")

    logo = param.String(doc="""
        URI of logo to add to the header (if local file, logo is
        base64 encoded as URI). Default is '', i.e. not shown.""")

    favicon = param.String(default=FAVICON_URL, doc="""
        URI of favicon to add to the document head (if local file, favicon is
        base64 encoded as URI).""")

    title = param.String(default="Panel Application", doc="""
        A title to show in the header. Also added to the document head
        meta settings and as the browser tab title.""")

    site = param.String(default="", doc="""
        Name of the site. Will be shown in the header and link to the
        'site_url'. Default is '', i.e. not shown.""")

    site_url = param.String(default="/", doc="""
        Url of the site and logo. Default is '/'.""")

    manifest = param.String(default=None, doc="""
        Manifest to add to site.""")

    meta_description = param.String(doc="""
        A meta description to add to the document head for search
        engine optimization. For example 'P.A. Nelson'.""")

    meta_keywords = param.String(doc="""
        Meta keywords to add to the document head for search engine
        optimization.""")

    meta_author = param.String(doc="""
        A meta author to add to the the document head for search
        engine optimization. For example 'P.A. Nelson'.""")

    meta_refresh = param.String(doc="""
        A meta refresh rate to add to the document head. For example
        '30' will instruct the browser to refresh every 30
        seconds. Default is '', i.e. no automatic refresh.""")

    meta_viewport = param.String(doc="""
        A meta viewport to add to the header.""")

    base_url = param.String(doc="""
        Specifies the base URL for all relative URLs in a
        page. Default is '', i.e. not the domain.""")

    base_target = param.ObjectSelector(default="_self",
        objects=["_blank", "_self", "_parent", "_top"], doc="""
        Specifies the base Target for all relative URLs in a page.""")

    header_background = param.String(doc="""
        Optional header background color override.""")

    header_color = param.String(doc="""
        Optional header text color override.""")

    theme = param.ClassSelector(class_=Theme, default=DefaultTheme,
                                constant=True, is_instance=False, instantiate=False)

    location = param.Boolean(default=True, readonly=True)

    _actions = param.ClassSelector(default=TemplateActions(), class_=TemplateActions)

    #############
    # Resources #
    #############

    # Resource locations for bundled resources
    _CDN: ClassVar[str] = CDN_DIST
    _LOCAL: ClassVar[str] = LOCAL_DIST

    # pathlib.Path pointing to local CSS file(s)
    _css: ClassVar[Path | str | List[Path | str] | None] = None

    # pathlib.Path pointing to local JS file(s)
    _js: ClassVar[Path | str | List[Path | str] | None] = None

    # pathlib.Path pointing to local Jinja2 template
    _template: ClassVar[Path | None] = None

    # External resources
    _resources: ClassVar[Dict[str, Dict[str, str]]] = {
        'css': {}, 'js': {}, 'js_modules': {}, 'tarball': {}
    }

    _modifiers: ClassVar[Dict[Type[Viewable], Dict[str, Any]]] = {}

    __abstract = True

    def __init__(self, **params):
        template = self._template.read_text()
        if 'header' not in params:
            params['header'] = ListLike()
        else:
            params['header'] = self._get_params(params['header'], self.param.header.class_)
        if 'main' not in params:
            params['main'] = ListLike()
        else:
            params['main'] = self._get_params(params['main'], self.param.main.class_)
        if 'sidebar' not in params:
            params['sidebar'] = ListLike()
        else:
            params['sidebar'] = self._get_params(params['sidebar'], self.param.sidebar.class_)
        if 'modal' not in params:
            params['modal'] = ListLike()
        else:
            params['modal'] = self._get_params(params['modal'], self.param.modal.class_)
        if 'theme' in params and isinstance(params['theme'], str):
            params['theme'] = THEMES[params['theme']]
        if 'favicon' in params and isinstance(params['favicon'], PurePath):
            params['favicon'] = str(params['favicon'])
        if 'notifications' not in params and config.notifications:
            params['notifications'] = state.notifications if state.curdoc else NotificationArea()
        super().__init__(template=template, **params)
        self._js_area = HTML(margin=0, width=0, height=0)
        if 'embed(roots.js_area)' in template:
            self._render_items['js_area'] = (self._js_area, [])
        if 'embed(roots.actions)' in template:
            self._render_items['actions'] = (self._actions, [])
        if 'embed(roots.notifications)' in template and self.notifications:
            self._render_items['notifications'] = (self.notifications, [])
            self._render_variables['notifications'] = True
        self._update_busy()
        self.main.param.watch(self._update_render_items, ['objects'])
        self.modal.param.watch(self._update_render_items, ['objects'])
        self.sidebar.param.watch(self._update_render_items, ['objects'])
        self.header.param.watch(self._update_render_items, ['objects'])
        self.main.param.trigger('objects')
        self.sidebar.param.trigger('objects')
        self.header.param.trigger('objects')
        self.modal.param.trigger('objects')

    def _init_doc(
        self, doc: Optional[Document] = None, comm: Optional['Comm'] = None,
        title: Optional[str]=None, notebook: bool = False, location: bool | Location = True
    ) -> Document:
        title = self.title if self.title != self.param.title.default else title
        if self.busy_indicator:
            state.sync_busy(self.busy_indicator)
        self._update_vars()
        document = super()._init_doc(doc, comm, title, notebook, location)
        if self.notifications:
            state._notifications[document] = self.notifications
        if self.theme:
            theme = self._get_theme()
            if theme and theme.bokeh_theme:
                document.theme = theme.bokeh_theme
        return document

    def _apply_hooks(self, viewable: Viewable, root: Model):
        super()._apply_hooks(viewable, root)
        theme = self._get_theme()
        if theme and theme.bokeh_theme and root.document:
            root.document.theme = theme.bokeh_theme
        return

    def _get_theme(self) -> Theme | None:
        for cls in type(self).__mro__:
            try:
                return self.theme.find_theme(cls)()
            except Exception:
                pass
        return None

    def _template_resources(self) -> ResourcesType:
        clsname = type(self).__name__
        name = clsname.lower()
        use_cdn = _settings.resources(default="server") != 'server'
        if use_cdn:
            dist_path = self._CDN
        elif state.rel_path:
            dist_path = f'{state.rel_path}/{self._LOCAL}'
        else:
            dist_path = f'{self._LOCAL}'

        # External resources
        css_files: Dict[str, str] = {}
        js_files: Dict[str, str] = {}
        js_modules: Dict[str, str] = {}
        resource_types: ResourcesType = {
            'css': css_files,
            'js': js_files,
            'js_modules': js_modules,
            'extra_css': list(self.config.raw_css),
            'raw_css': []
        }

        resolved_resources: List[Literal['css', 'js', 'js_modules']] = ['css', 'js', 'js_modules']
        for resource_type in resolved_resources:
            if resource_type not in self._resources:
                continue
            resource_files = resource_types[resource_type]
            shared = list((CSS_URLS if resource_type == 'css' else JS_URLS).values())
            for rname, resource in self._resources[resource_type].items():
                if resource.startswith(CDN_DIST):
                    resource_path = resource.replace(f'{CDN_DIST}bundled/', '')
                elif resource.startswith(config.npm_cdn):
                    resource_path = resource.replace(config.npm_cdn, '')[1:]
                else:
                    resource_path = url_path(resource)
                if resource in shared:
                    prefixed = resource_path
                else:
                    rtype = 'css' if resource_type == 'css' else 'js'
                    prefixed = f'{rtype}/{resource_path}'
                if resource_type == 'js_modules' and not (state.rel_path or use_cdn):
                    prefixed_dist = f'./{dist_path}'
                else:
                    prefixed_dist = dist_path
                bundlepath = BUNDLE_DIR / prefixed.replace('/', os.path.sep)
                if bundlepath:
                    resource_files[rname] = f'{prefixed_dist}bundled/{prefixed}'
                elif isurl(resource):
                    resource_files[rname] = resource
                elif resolve_custom_path(self, resource):
                    resource_files[rname] = component_resource_path(
                        self, f'_resources/{resource_type}', resource
                    )

        for name, js in self.config.js_files.items():
            if not '//' in js and state.rel_path:
                js = f'{state.rel_path}/{js}'
            js_files[name] = js
        for name, js in self.config.js_modules.items():
            if not '//' in js and state.rel_path:
                js = f'{state.rel_path}/{js}'
            js_modules[name] = js

        extra_css = resource_types['extra_css']
        for css in list(self.config.css_files):
            if not '//' in css and state.rel_path:
                css = f'{state.rel_path}/{css}'
            extra_css.append(css)

        # CSS files
        base_css = self._css
        if not isinstance(base_css, list):
            base_css = [base_css] if base_css else []
        for css in base_css:
            tmpl_name = name
            for cls in type(self).__mro__[1:-5]:
                if not issubclass(cls, BasicTemplate):
                    continue
                elif cls._css is None:
                    break
                tmpl_css = cls._css if isinstance(cls._css, list) else [cls._css]
                if css in tmpl_css:
                    tmpl_name = cls.__name__.lower()

            css_file = os.path.basename(css)
            if (BUNDLE_DIR / tmpl_name / css_file).is_file():
                css_files[f'base_{css_file}'] = dist_path + f'bundled/{tmpl_name}/{css_file}'
            elif isurl(css):
                css_files[f'base_{css_file}'] = css
            elif resolve_custom_path(self, css):
                css_files[f'base_{css_file}' ] = component_resource_path(self, '_css', css)

        # JS files
        base_js = self._js
        if not isinstance(base_js, list):
            base_js = [base_js] if base_js else []
        for js in base_js:
            tmpl_name = name
            for cls in type(self).__mro__[1:-5]:
                if not issubclass(cls, BasicTemplate):
                    continue
                elif cls._js is None:
                    break
                tmpl_js = cls._js if isinstance(cls._js, list) else [cls._js]
                if js in tmpl_js:
                    tmpl_name = cls.__name__.lower()
            js_name = os.path.basename(js)
            if (BUNDLE_DIR / tmpl_name / js_name).is_file():
                js_files[f'base_{js_name}'] = dist_path + f'bundled/{tmpl_name}/{js_name}'
            elif isurl(js):
                js_files[f'base_{js_name}'] = js
            elif resolve_custom_path(self, js):
                js_files[f'base_{js_name}'] = component_resource_path(self, '_js', js)

        theme = self._get_theme()
        if not theme:
            return resource_types
        if theme.base_css:
            basename = os.path.basename(theme.base_css)
            owner = type(theme).param.base_css.owner
            owner_name = owner.__name__.lower()
            if (BUNDLE_DIR / owner_name / basename).is_file():
                css_files['theme_base'] = dist_path + f'bundled/{owner_name}/{basename}'
            elif isurl(theme.base_css):
                css_files['theme_base'] = theme.base_css
            elif resolve_custom_path(theme, theme.base_css):
                css_files['theme_base'] = component_resource_path(owner, 'base_css', theme.base_css)
        if theme.css:
            basename = os.path.basename(theme.css)
            if (BUNDLE_DIR / name / basename).is_file():
                css_files['theme'] = dist_path + f'bundled/{name}/{basename}'
            elif isurl(theme.css):
                css_files['theme'] = theme.css
            elif resolve_custom_path(theme, theme.css):
                css_files['theme'] = component_resource_path(theme, 'css', theme.css)
        return resource_types

    def _update_vars(self, *args) -> None:
        self._render_variables['app_title'] = self.title
        self._render_variables['meta_name'] = self.title
        self._render_variables['site_title'] = self.site
        self._render_variables['site_url'] = self.site_url
        self._render_variables['manifest'] = self.manifest
        self._render_variables['meta_description'] = self.meta_description
        self._render_variables['meta_keywords'] = self.meta_keywords
        self._render_variables['meta_author'] = self.meta_author
        self._render_variables['meta_refresh'] = self.meta_refresh
        self._render_variables['meta_viewport'] = self.meta_viewport
        self._render_variables['base_url'] = self.base_url
        self._render_variables['base_target'] = self.base_target
        if os.path.isfile(self.logo):
            img = _panel(self.logo)
            if not isinstance(img, ImageBase):
                raise ValueError(f"Could not determine file type of logo: {self.logo}.")
            logo = img._b64()
        else:
            logo = self.logo
        if os.path.isfile(self.favicon):
            img = _panel(self.favicon)
            if not isinstance(img, ImageBase):
                raise ValueError(f"Could not determine file type of favicon: {self.favicon}.")
            favicon = img._b64()
        else:
            if _settings.resources(default='server') == 'cdn' and self.favicon == FAVICON_URL:
                favicon = DOC_DIST + "icons/favicon.ico"
            else:
                favicon = self.favicon
        self._render_variables['template_resources'] = self._template_resources()
        self._render_variables['app_logo'] = logo
        self._render_variables['app_favicon'] = favicon
        self._render_variables['app_favicon_type'] = self._get_favicon_type(self.favicon)
        self._render_variables['header_background'] = self.header_background
        self._render_variables['header_color'] = self.header_color
        self._render_variables['main_max_width'] = self.main_max_width
        self._render_variables['sidebar_width'] = self.sidebar_width

    def _update_busy(self) -> None:
        if self.busy_indicator:
            self._render_items['busy_indicator'] = (self.busy_indicator, [])
        elif 'busy_indicator' in self._render_items:
            del self._render_items['busy_indicator']
        self._render_variables['busy'] = self.busy_indicator is not None

    def _update_render_items(self, event: param.parameterized.Event) -> None:
        if event.obj is self and event.name == 'busy_indicator':
            return self._update_busy()
        if event.obj is self.main:
            tag = 'main'
        elif event.obj is self.sidebar:
            tag = 'nav'
        elif event.obj is self.header:
            tag = 'header'
        elif event.obj is self.modal:
            tag = 'modal'

        old = event.old if isinstance(event.old, list) else list(event.old.values())
        for obj in old:
            ref = str(id(obj))
            if ref in self._render_items:
                del self._render_items[ref]

        new = event.new if isinstance(event.new, list) else event.new.values()
        theme = self._get_theme()
        if theme:
            bk_theme = theme.bokeh_theme
            for o in new:
                if o in old:
                    continue
                for hvpane in o.select(HoloViews):
                    if bk_theme:
                        hvpane.theme = bk_theme

        labels = {}
        for obj in new:
            ref = str(id(obj))
            if obj.name.startswith(type(obj).__name__):
                labels[ref] = 'Content'
            else:
                labels[ref] = obj.name
            self._render_items[ref] = (obj, [tag])
        tags = [tags for _, tags in self._render_items.values()]
        self._render_variables['nav'] = any('nav' in ts for ts in tags)
        self._render_variables['header'] = any('header' in ts for ts in tags)
        self._render_variables['root_labels'] = labels

    def _server_destroy(self, session_context: BokehSessionContext):
        super()._server_destroy(session_context)
        if not self._documents and self.busy_indicator in state._indicators:
            state._indicators.remove(self.busy_indicator)

    def open_modal(self) -> None:
        """
        Opens the modal area
        """
        self._actions.open_modal += 1

    def close_modal(self) -> None:
        """
        Closes the modal area
        """
        self._actions.close_modal += 1

    @staticmethod
    def _get_favicon_type(favicon) -> str:
        if not favicon:
            return ""
        elif favicon.endswith(".png"):
            return "image/png"
        elif favicon.endswith("jpg"):
            return "image/jpg"
        elif favicon.endswith("gif"):
            return "image/gif"
        elif favicon.endswith("svg"):
            return "image/svg"
        elif favicon.endswith("ico"):
            return "image/x-icon"
        else:
            raise ValueError("favicon type not supported.")

    @staticmethod
    def _get_params(value, class_):
        if isinstance(value, class_):
            return value
        if isinstance(value, tuple):
            value = [*value]
        elif not isinstance(value, list):
            value = [value]

        # Important to fx. convert @param.depends functions
        value = [_panel(item) for item in value]

        if class_ is ListLike:
            return ListLike(objects=value)
        if class_ is GridSpec:
            grid = GridSpec(ncols=12, mode='override')
            for index, item in enumerate(value):
                grid[index, :]=item
            return grid

        return value


class Template(BaseTemplate):
    """
    A Template is a high-level component to render multiple Panel
    objects into a single HTML document defined through a Jinja2
    template. The Template object is given a Jinja2 template and then
    allows populating this template by adding Panel objects, which are
    given unique names. These unique names may then be referenced in
    the template to insert the rendered Panel object at a specific
    location. For instance, given a Jinja2 template that defines roots
    A and B like this:

        <div> {{ embed(roots.A) }} </div>
        <div> {{ embed(roots.B) }} </div>

    We can then populate the template by adding panel 'A' and 'B' to
    the Template object:

        template.add_panel('A', pn.panel('A'))
        template.add_panel('B', pn.panel('B'))

    Once a template has been fully populated it can be rendered using
    the same API as other Panel objects. Note that all roots that have
    been declared using the {{ embed(roots.A) }} syntax in the Jinja2
    template must be defined when rendered.

    Since embedding complex CSS frameworks inside a notebook can have
    undesirable side-effects and a notebook does not afford the same
    amount of screen space a Template may given separate template
    and nb_template objects. This allows for different layouts when
    served as a standalone server and when used in the notebook.
    """

    def __init__(
        self, template: str | _Template, nb_template: str | _Template | None = None,
        items: Optional[Dict[str, Any]] = None, **params
    ):
        super().__init__(template=template, nb_template=nb_template, items=items, **params)
        items = {} if items is None else items
        for name, item in items.items():
            self.add_panel(name, item)

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def add_panel(self, name: str, panel: Viewable, tags: List[str] = []) -> None:
        """
        Add panels to the Template, which may then be referenced by
        the given name using the jinja2 embed macro.

        Arguments
        ---------
        name : str
          The name to refer to the panel by in the template
        panel : panel.Viewable
          A Panel component to embed in the template.
        """
        if name in self._render_items:
            raise ValueError('The name %s has already been used for '
                             'another panel. Ensure each panel '
                             'has a unique name by which it can be '
                             'referenced in the template.' % name)
        self._render_items[name] = (_panel(panel), tags)
        self._layout[0].object = repr(self) # type: ignore

    def add_variable(self, name: str, value: Any) -> None:
        """
        Add parameters to the template, which may then be referenced
        by the given name in the Jinja2 template.

        Arguments
        ---------
        name : str
          The name to refer to the panel by in the template
        value : object
          Any valid Jinja2 variable type.
        """
        if name in self._render_variables:
            raise ValueError('The name %s has already been used for '
                             'another variable. Ensure each variable '
                             'has a unique name by which it can be '
                             'referenced in the template.' % name)
        self._render_variables[name] = value
