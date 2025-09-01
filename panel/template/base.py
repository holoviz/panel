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
    IO, TYPE_CHECKING, Any, ClassVar, Literal, cast,
)

import jinja2
import param

from bokeh.document.document import Document
from bokeh.models import LayoutDOM
from bokeh.settings import settings as _settings
from pyviz_comms import JupyterCommManager as _JupyterCommManager

from ..config import _base_config, config, panel_extension
from ..io.document import init_doc
from ..io.model import add_to_doc
from ..io.notebook import render_template
from ..io.notifications import NotificationArea, NotificationAreaBase
from ..io.resources import (
    BUNDLE_DIR, CDN_DIST, JS_VERSION, ResourceComponent, _env,
    component_resource_path, get_dist_path, loading_css, parse_template,
    resolve_custom_path, use_cdn,
)
from ..io.save import save
from ..io.state import set_curdoc, state
from ..layout import Column, GridSpec, ListLike
from ..models.comm_manager import CommManager
from ..pane import (
    HTML, HoloViews, Str, panel as _panel,
)
from ..pane.image import ImageBase
from ..reactive import ReactiveHTML
from ..theme.base import (
    THEMES, DefaultTheme, Design, Theme,
)
from ..util import isurl
from ..viewable import (
    MimeRenderMixin, Renderable, ServableMixin, Viewable,
)
from ..widgets import Button
from ..widgets.indicators import BooleanIndicator, LoadingSpinner

if TYPE_CHECKING:
    from bokeh.model import Model
    from bokeh.server.contexts import BokehSessionContext
    from jinja2 import Template as _Template
    from pyviz_comms import Comm
    from typing_extensions import Self

    from ..io.location import Location
    from ..io.resources import ResourcesType


_server_info: str = (
    '<b>Running server:</b> <a target="_blank" href="https://localhost:{port}">'
    'https://localhost:{port}</a>'
)

FAVICON_URL: str = "/static/extensions/panel/images/favicon.ico"


class BaseTemplate(param.Parameterized, MimeRenderMixin, ServableMixin, ResourceComponent):

    config = param.ClassSelector(default=_base_config(), class_=_base_config,
                                 constant=True, doc="""
        Configuration object declaring custom CSS and JS files to load
        specifically for this template.""")

    design = param.ClassSelector(class_=Design, default=Design,
                                 is_instance=False, instantiate=False, doc="""
        A Design applies themes to a template.""")

    location = param.Boolean(default=False, doc="""
        Whether to add a Location component to this Template.
        Note if this is set to true, the Jinja2 template must
        either insert all available roots or explicitly embed
        the location root with : {{ embed(roots.location) }}.""")

    theme = param.ClassSelector(class_=Theme, default=DefaultTheme,
                                constant=True, is_instance=False, instantiate=False)

    # Dictionary of property overrides by Viewable type
    modifiers: ClassVar[dict[type[Viewable], dict[str, Any]]] = {}

    #############
    # Resources #
    #############

    # pathlib.Path pointing to local CSS file(s)
    _css: ClassVar[list[Path | str]] = []

    # pathlib.Path pointing to local JS file(s)
    _js: ClassVar[Path | str | list[Path | str] | None] = None

    # External resources
    _resources = {
        'css': {}, 'js': {}, 'js_modules': {}, 'tarball': {}
    }

    __abstract = True

    def __init__(
        self, template: str | _Template, items=None,
        nb_template: str | _Template | None = None, **params
    ):
        config_params = {
            p: v for p, v in params.items() if p in _base_config.param
        }
        self._render_items: dict[str, tuple[Renderable, list[str]]]  = {}
        self._render_variables: dict[str, Any] = {}
        super().__init__(**{
            p: v for p, v in params.items() if p not in _base_config.param or p == 'name'
        })
        self.config.param.update(config_params)
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
        self._documents: list[Document] = []
        self._refs: dict[Document, str] = {}
        self._server = None
        self._layout = self._build_layout()
        self._setup_design()

    @param.depends('design', watch=True)
    def _setup_design(self):
        self._design = self.design(theme=self.theme)

    def _update_vars(self, *args) -> None:
        """
        Updates the render variables before the template is rendered.
        """

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

    def _apply_root(self, name: str, model: Model, tags: list[str]) -> None:
        pass

    def _server_destroy(self, session_context: BokehSessionContext):
        doc = session_context._document
        if doc in state._templates:
            del state._templates[doc]
        ref = self._refs.pop(doc, None)
        if ref:
            state._fake_roots.remove(ref)
        self._documents.remove(doc)

    def _init_doc(
        self, doc: Document | None = None, comm: Comm | None = None,
        title: str | None = None, notebook: bool = False,
        location: bool | Location = True
    ):
        # Initialize document
        document = init_doc(doc or state.curdoc)

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
        preprocess_root = col.get_root(document, comm, preprocess=False)
        col._hooks.append(self._design._apply_hooks)
        ref = preprocess_root.ref['id']

        # Add all render items to the document
        objs, models = [], []
        stylesheets, sizing_modes = {}, {}
        tracked_models: set[Model] = set()
        for name, (obj, tags) in self._render_items.items():
            # Render root without pre-processing
            with config.set(design=self.design):
                model = obj.get_root(document, comm, preprocess=False)
            model.name = name
            model.tags = model.tags + [tag for tag in tags if tag not in model.tags]
            mref = model.ref['id']
            if isinstance(model, LayoutDOM):
                sizing_modes[mref] = model.sizing_mode
                if self._design._apply_hooks not in obj._hooks:
                    obj._hooks.append(self._design._apply_hooks)

                # Alias model ref with the fake root ref to ensure that
                # pre-processor correctly operates on fake root
                for sub in obj.select(Viewable):
                    submodel = sub._models.get(mref)
                    for stylesheet in getattr(sub, '_stylesheets', []):
                        if isinstance(stylesheet, PurePath):
                            stylesheet = str(stylesheet)
                        if not stylesheet.endswith('.css'):
                            continue
                        sts_name = f'extra_{os.path.basename(stylesheet)}'
                        stylesheets[sts_name] = stylesheet
                    if submodel is None:
                        continue
                    sub._models[ref] = submodel
                    if isinstance(sub, HoloViews) and mref in sub._plots:
                        sub._plots[ref] = sub._plots.get(mref)

                # Apply any template specific hooks to root
                self._apply_root(name, model, tags)

                # Add document
                obj._documents[document] = model
                objs.append(obj)
                models.append(model)

            tracked_models |= add_to_doc(model, document, hold=bool(comm), skip=tracked_models)
            document.on_session_destroyed(obj._server_destroy) # type: ignore

        # Here we ensure that the preprocessor is run across all roots
        # and set up session cleanup hooks for the fake root.
        state._fake_roots.append(ref) # Ensure no update is run
        state._views[ref] = (col, preprocess_root, document, comm)
        col.objects = objs
        preprocess_root.children[:] = models
        preprocess_root.document = document
        self._design.apply(col, preprocess_root, isolated=False)
        col._preprocess(preprocess_root)
        col._documents[document] = preprocess_root
        document.on_session_destroyed(col._server_destroy) # type: ignore

        # Apply the jinja2 template and update template variables
        if notebook:
            document.template = self.nb_template
        else:
            document.template = self.template

        self._update_vars()
        resources = self.resolve_resources(extras={'css': stylesheets})
        document._template_variables['template_resources'] = resources
        document._template_variables['sizing_modes'] = sizing_modes
        document._template_variables.update(self._render_variables)
        return document

    def _repr_mimebundle_(
        self, include=None, exclude=None
    ) -> tuple[dict[str, str], dict[str, dict[str, str]]] | None:
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
            on_stdout=partial(self._on_stdout, ref),
            on_open=lambda _: comm.init()
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

    def resolve_resources(
        self,
        cdn: bool | Literal['auto'] = 'auto',
        extras: dict[str, dict[str, str]] | None = None
    ) -> ResourcesType:
        """
        Resolves the resources required for this template component.

        Parameters
        ----------
        cdn: bool | Literal['auto']
            Whether to load resources from CDN or local server. If set
            to 'auto' value will be automatically determine based on
            global settings.
        extras: dict[str, dict[str, str]] | None
            Additional resources to add to the bundle. Valid resource
            types include js, js_modules and css.

        Returns
        -------
        Dictionary containing JS and CSS resources.
        """
        cls = type(self)
        resource_types = super().resolve_resources(cdn=cdn, extras=extras)
        js_files = resource_types['js']
        js_modules = resource_types['js_modules']
        css_files = resource_types['css']
        raw_css = resource_types['raw_css']

        clsname = cls.__name__
        name = clsname.lower()
        cdn = use_cdn() if cdn == 'auto' else cdn
        dist_path = get_dist_path(cdn=cdn)
        version_suffix = f'?v={JS_VERSION}'

        css_files['loading'] = f'{dist_path}css/loading.css{version_suffix}'
        raw_css.extend(list(self.config.raw_css) + [loading_css(
            config.loading_spinner, config.loading_color, config.loading_max_height
        )])
        for rname, res in self._design.resolve_resources(cdn).items():
            if isinstance(res, dict):
                resource_types[rname].update(res)  # type: ignore
            else:
                resource_types[rname] += [  # type: ignore
                    r for r in res if r not in resource_types[rname]  # type: ignore
                ]

        for rname, js in self.config.js_files.items():
            if '//' not in js and state.rel_path:
                js = f'{state.rel_path}/{js}'
            js_files[rname] = js
        for rname, js in self.config.js_modules.items():
            if '//' not in js and state.rel_path:
                js = f'{state.rel_path}/{js}'
            js_modules[rname] = js
        for i, css in enumerate(list(self.config.css_files)):
            if '//' not in css and state.rel_path:
                css = f'{state.rel_path}/{css}'
            css_files[f'config_{i}'] = css

        # CSS files
        base_css = self._css
        if not isinstance(base_css, list):
            base_css = [base_css] if base_css else []
        for css in base_css:
            tmpl_name = name
            for scls in cls.__mro__[1:]:
                if not issubclass(scls, BaseTemplate):
                    continue
                elif scls._css is None:
                    break
                tmpl_css = scls._css if isinstance(scls._css, list) else [scls._css]  # type: ignore
                if css in tmpl_css:
                    tmpl_name = scls.__name__.lower()

            css_file = os.path.basename(css)
            if (BUNDLE_DIR / tmpl_name / css_file).is_file():
                css_files[f'base_{css_file}'] = f'{dist_path}bundled/{tmpl_name}/{css_file}{version_suffix}'
            elif isurl(css):
                css_files[f'base_{css_file}'] = cast("str", css)
            elif resolve_custom_path(self, css):
                css_files[f'base_{css_file}' ] = component_resource_path(self, '_css', css)

        # JS files
        base_js = self._js
        if not isinstance(base_js, list):
            base_js = [base_js] if base_js else []
        for js in base_js:
            tmpl_name = name
            for cls in type(self).__mro__[1:-5]:
                if not issubclass(cls, BaseTemplate):
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
                js_files[f'base_{js_name}'] = cast("str", js)
            elif resolve_custom_path(self, js):
                js_files[f'base_{js_name}'] = component_resource_path(self, '_js', js)

        return resource_types

    def save(
        self, filename: str | os.PathLike | IO, title: str | None = None,
        resources=None, embed: bool = False, max_states: int = 1000,
        max_opts: int = 3, embed_json: bool = False, json_prefix: str='',
        save_path: str='./', load_path: str | None = None
    ) -> None:
        """
        Saves Panel objects to file.

        Parameters
        ----------
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
        self, doc: Document | None = None, title: str | None = None,
        location: bool | Location = True
    ) -> Document:
        """
        Returns a servable Document with the template attached.

        Parameters
        ----------
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
          The Bokeh document the panel was attached to.
        """
        return self._init_doc(doc, title=title, location=location)

    def servable(
        self, title: str | None = None, location: bool | Location = True,
        area: str = 'main', target: str | None = None
    ) -> Self:
        """
        Serves the template and returns self to allow it to display
        itself in a notebook context.

        Parameters
        ----------
        title : str
          A string title to give the Document (if served as an app)
        location : boolean or panel.io.location.Location
          Whether to create a Location component to observe and
          set the URL location.
        area: str (deprecated)
          The area of a template to add the component too. Only has an
          effect if pn.config.template has been set.
        target: str
          Target area to write to. If a template has been configured
          on pn.config.template this refers to the target area in the
          template while in pyodide this refers to the ID of the DOM
          node to write to.

        Returns
        -------
        The template object
        """
        doc = state.curdoc
        if doc and doc.session_context and config.template:
            raise RuntimeError(
                'Cannot mark template as servable if a global template '
                'is defined. Either explicitly construct a template and '
                'serve it OR set `pn.config.template`, whether directly '
                'or via `pn.extension(template=...)`, not both.'
            )
        return super().servable(title, location, area, target)

    def select(self, selector=None):
        """
        Iterates over the Template and any potential children in the
        applying the Selector.

        Parameters
        ----------
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

    open_modal = param.Integer(default=0, doc="""
        The number of times the open modal action has been triggered.
        This is used to trigger the open modal script.""")

    close_modal = param.Integer(default=0, doc="""
        The number of times the close modal action has been triggered.
        This is used to trigger the close modal script.""")

    _template: ClassVar[str] = ""

    _scripts: ClassVar[dict[str, list[str] | str]] = {
        'open_modal': ["""
          document.getElementById('pn-Modal').style.display = 'block'
          window.dispatchEvent(new Event('resize'));
        """],
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

    busy_indicator = param.ClassSelector(default=LoadingSpinner(width=20, height=20),
                                         class_=BooleanIndicator, constant=True,
                                         allow_None=True, doc="""
        Visual indicator of application busy state.""")

    collapsed_sidebar = param.Selector(default=False, constant=True, doc="""
        Whether the sidebar (if present) is initially collapsed.""")

    header = param.ClassSelector(class_=ListLike, constant=True, doc="""
        A list-like container which populates the header bar.""")

    main = param.ClassSelector(class_=ListLike, constant=True, doc="""
        A list-like container which populates the main area.""")

    main_max_width = param.String(default="", doc="""
        The maximum width of the main area. For example '800px' or '80%'.
        If the string is '' (default) no max width is set.""")

    sidebar = param.ClassSelector(class_=ListLike, constant=True, doc="""
        A list-like container which populates the sidebar.""")

    sidebar_width = param.Integer(default=330, doc="""
        The width of the sidebar in pixels. Default is 330.""")

    modal = param.ClassSelector(class_=ListLike, constant=True, doc="""
        A list-like container which populates the modal""")

    notifications = param.ClassSelector(class_=NotificationAreaBase, constant=True, doc="""
        The NotificationArea instance attached to this template.
        Automatically added if config.notifications is set, but may
        also be provided explicitly.""")

    logo = param.String(doc="""
        URI of logo to add to the header (if local file, logo is
        base64 encoded as URI). Default is '', i.e. not shown.""")

    favicon = param.String(default=None, doc="""
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

    base_target = param.Selector(default="_self",
        objects=["_blank", "_self", "_parent", "_top"], doc="""
        Specifies the base Target for all relative URLs in a page.""")

    header_background = param.String(doc="""
        Optional header background color override.""")

    header_color = param.String(doc="""
        Optional header text color override.""")

    location = param.Boolean(default=True, readonly=True)

    _actions = param.ClassSelector(default=TemplateActions(), class_=TemplateActions)

    #############
    # Resources #
    #############

    # pathlib.Path pointing to local Jinja2 template
    _template: ClassVar[Path | None] = None

    __abstract = True

    def __init__(self, **params):
        tmpl_string = self._template.read_text(encoding='utf-8')
        try:
            template = _env.get_template(str(self._template.relative_to(Path(__file__).parent)))
        except (jinja2.exceptions.TemplateNotFound, ValueError):
            template = parse_template(tmpl_string)

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
        if 'theme' in params:
            if isinstance(params['theme'], str):
                params['theme'] = THEMES[params['theme']]
        else:
            params['theme'] = THEMES[config.theme]
        if 'favicon' in params and isinstance(params['favicon'], PurePath):
            params['favicon'] = str(params['favicon'])
        if 'notifications' not in params and config.notifications:
            params['notifications'] = state.notifications if state.curdoc else NotificationArea()

        super().__init__(template=template, **params)
        self._js_area = HTML(margin=0, width=0, height=0)
        state_roots = '{% block state_roots %}' in tmpl_string
        if state_roots or 'embed(roots.js_area)' in tmpl_string:
            self._render_items['js_area'] = (self._js_area, [])
        if state_roots or 'embed(roots.actions)' in tmpl_string:
            self._render_items['actions'] = (self._actions, [])
        if (state_roots or 'embed(roots.notifications)' in tmpl_string) and self.notifications:
            self._render_items['notifications'] = (self.notifications, [])
            self._render_variables['notifications'] = True
        if config.browser_info and ('embed(roots.browser_info)' in tmpl_string or state_roots) and state.browser_info:
            self._render_items['browser_info'] = (state.browser_info, [])
            self._render_variables['browser_info'] = True
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
        self, doc: Document | None = None, comm: Comm | None = None,
        title: str | None=None, notebook: bool = False, location: bool | Location = True
    ) -> Document:
        title = self.title if self.title != self.param.title.default else title
        if self.busy_indicator:
            state.sync_busy(self.busy_indicator)
        document = super()._init_doc(doc, comm, title, notebook, location)
        if self.notifications:
            state._notifications[document] = self.notifications
        if self._design.theme.bokeh_theme:
            document.theme = self._design.theme.bokeh_theme
        with set_curdoc(document):
            config.design = type(self._design)
        return document

    def _update_vars(self, *args) -> None:
        super()._update_vars(*args)
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
            imgdata = img._data(img.object)
            if imgdata:
                logo = img._b64(imgdata)
            else:
                raise ValueError(f"Could not embed logo {self.logo}.")
        else:
            logo = self.logo
        if self.favicon and os.path.isfile(self.favicon):
            img = _panel(self.favicon)
            if not isinstance(img, ImageBase):
                raise ValueError(f"Could not determine file type of favicon: {self.favicon}.")
            imgdata = img._data(img.object)
            if imgdata:
                favicon = img._b64(imgdata)
            else:
                raise ValueError(f"Could not embed favicon {self.favicon}.")
        elif _settings.resources(default='server') == 'cdn' and self.favicon == FAVICON_URL:
            favicon = CDN_DIST + "images/favicon.ico"
        elif self.favicon:
            favicon = self.favicon
        else:
            favicon = (f"{state.rel_path}/" if state.rel_path else "./") + "favicon.ico"
        self._render_variables['app_logo'] = logo
        if favicon:
            self._render_variables['app_favicon'] = favicon
            self._render_variables['app_favicon_type'] = self._get_favicon_type(self.favicon)
        self._render_variables['header_background'] = self.header_background
        self._render_variables['header_color'] = self.header_color
        self._render_variables['main_max_width'] = self.main_max_width
        self._render_variables['sidebar_width'] = self.sidebar_width
        self._render_variables['theme'] = self._design.theme
        self._render_variables['collapsed_sidebar'] = self.collapsed_sidebar

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
            ref = f'{tag}-{str(id(obj))}'
            if ref in self._render_items:
                del self._render_items[ref]

        new = event.new if isinstance(event.new, list) else event.new.values()
        if self._design.theme.bokeh_theme:
            for o in new:
                if o in old:
                    continue
                for hvpane in o.select(HoloViews):
                    hvpane.theme = self._design.theme.bokeh_theme

        labels = {}
        for obj in new:
            ref = f'{tag}-{str(id(obj))}'
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
        items: dict[str, Any] | None = None, **params
    ):
        super().__init__(template=template, nb_template=nb_template, items=items, **params)
        items = {} if items is None else items
        for name, item in items.items():
            self.add_panel(name, item)

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def add_panel(self, name: str, panel: Any, tags: list[str] = []) -> None:
        """
        Add panels to the Template, which may then be referenced by
        the given name using the jinja2 embed macro.

        Parameters
        ----------
        name : str
          The name to refer to the panel by in the template
        panel : panel.Viewable
          A Panel component to embed in the template.
        """
        if name in self._render_items:
            raise ValueError(f'The name {name} has already been used for '
                             'another panel. Ensure each panel '
                             'has a unique name by which it can be '
                             'referenced in the template.')
        rendered = _panel(panel)
        if not isinstance(rendered, Viewable):
            raise ValueError(f"Cannot add {type(panel).__name__!r} type")
        self._render_items[name] = (rendered, tags)
        self._layout[0].object = repr(self) # type: ignore

    def add_variable(self, name: str, value: Any) -> None:
        """
        Add parameters to the template, which may then be referenced
        by the given name in the Jinja2 template.

        Parameters
        ----------
        name : str
          The name to refer to the panel by in the template
        value : object
          Any valid Jinja2 variable type.
        """
        if name in self._render_variables:
            raise ValueError(f'The name {name} has already been used for '
                             'another variable. Ensure each variable '
                             'has a unique name by which it can be '
                             'referenced in the template.')
        self._render_variables[name] = value
