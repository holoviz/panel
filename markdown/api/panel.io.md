# panel.io package

## Submodules

- [panel.io.admin
  module](panel.io.admin.md)
  - [Data](panel.io.admin.md#panel.io.admin.Data)
  - [LogDataHandler](panel.io.admin.md#panel.io.admin.LogDataHandler)
    - [LogDataHandler.emit()](panel.io.admin.md#panel.io.admin.LogDataHandler.emit)
  - [LogFilter](panel.io.admin.md#panel.io.admin.LogFilter)
    - [LogFilter.filter()](panel.io.admin.md#panel.io.admin.LogFilter.filter)
- [panel.io.application module](panel.io.application.md)
  - [Application](panel.io.application.md#panel.io.application.Application)
    - [Application.add()](panel.io.application.md#panel.io.application.Application.add)
    - [Application.initialize_document()](panel.io.application.md#panel.io.application.Application.initialize_document)
    - [Application.on_session_created()](panel.io.application.md#panel.io.application.Application.on_session_created)
    - [Application.process_request()](panel.io.application.md#panel.io.application.Application.process_request)
  - [build_applications()](panel.io.application.md#panel.io.application.build_applications)
- [panel.io.browser module](panel.io.browser.md)
  - [BrowserInfo](panel.io.browser.md#panel.io.browser.BrowserInfo)
    - [BrowserInfo.get_root()](panel.io.browser.md#panel.io.browser.BrowserInfo.get_root)
- [panel.io.cache
  module](panel.io.cache.md)
  - [cache()](panel.io.cache.md#panel.io.cache.cache)
  - [compute_hash()](panel.io.cache.md#panel.io.cache.compute_hash)
  - [is_equal()](panel.io.cache.md#panel.io.cache.is_equal)
- [panel.io.callbacks module](panel.io.callbacks.md)
  - [PeriodicCallback](panel.io.callbacks.md#panel.io.callbacks.PeriodicCallback)
    - [PeriodicCallback.start()](panel.io.callbacks.md#panel.io.callbacks.PeriodicCallback.start)
    - [PeriodicCallback.stop()](panel.io.callbacks.md#panel.io.callbacks.PeriodicCallback.stop)
- [panel.io.compile module](panel.io.compile.md)
  - [BuildError](panel.io.compile.md#panel.io.compile.BuildError)
  - [compile_components()](panel.io.compile.md#panel.io.compile.compile_components)
  - [extract_dependencies()](panel.io.compile.md#panel.io.compile.extract_dependencies)
  - [find_components()](panel.io.compile.md#panel.io.compile.find_components)
  - [find_module_bundles()](panel.io.compile.md#panel.io.compile.find_module_bundles)
  - [generate_project()](panel.io.compile.md#panel.io.compile.generate_project)
  - [merge_exports()](panel.io.compile.md#panel.io.compile.merge_exports)
  - [packages_from_code()](panel.io.compile.md#panel.io.compile.packages_from_code)
  - [packages_from_importmap()](panel.io.compile.md#panel.io.compile.packages_from_importmap)
  - [replace_imports()](panel.io.compile.md#panel.io.compile.replace_imports)
- [panel.io.convert module](panel.io.convert.md)
  - [DummyRequirement](panel.io.convert.md#panel.io.convert.DummyRequirement)
  - [collect_python_requirements()](panel.io.convert.md#panel.io.convert.collect_python_requirements)
  - [convert_apps()](panel.io.convert.md#panel.io.convert.convert_apps)
  - [pack_files()](panel.io.convert.md#panel.io.convert.pack_files)
  - [script_to_html()](panel.io.convert.md#panel.io.convert.script_to_html)
- [panel.io.datamodel module](panel.io.datamodel.md)
  - [Parameterized](panel.io.datamodel.md#panel.io.datamodel.Parameterized)
  - [ParameterizedList](panel.io.datamodel.md#panel.io.datamodel.ParameterizedList)
    - [ParameterizedList.validate()](panel.io.datamodel.md#panel.io.datamodel.ParameterizedList.validate)
  - [PolarsDataFrame](panel.io.datamodel.md#panel.io.datamodel.PolarsDataFrame)
    - [PolarsDataFrame.validate()](panel.io.datamodel.md#panel.io.datamodel.PolarsDataFrame.validate)
  - [construct_data_model()](panel.io.datamodel.md#panel.io.datamodel.construct_data_model)
  - [create_linked_datamodel()](panel.io.datamodel.md#panel.io.datamodel.create_linked_datamodel)
- [panel.io.django module](panel.io.django.md)
- [panel.io.document module](panel.io.document.md)
  - [MockSessionContext](panel.io.document.md#panel.io.document.MockSessionContext)
    - [MockSessionContext.destroyed](panel.io.document.md#panel.io.document.MockSessionContext.destroyed)
    - [MockSessionContext.with_locked_document()](panel.io.document.md#panel.io.document.MockSessionContext.with_locked_document)
  - [Request](panel.io.document.md#panel.io.document.Request)
  - [freeze_doc()](panel.io.document.md#panel.io.document.freeze_doc)
  - [hold()](panel.io.document.md#panel.io.document.hold)
  - [immediate_dispatch()](panel.io.document.md#panel.io.document.immediate_dispatch)
  - [retrigger_events()](panel.io.document.md#panel.io.document.retrigger_events)
  - [unlocked()](panel.io.document.md#panel.io.document.unlocked)
  - [with_lock()](panel.io.document.md#panel.io.document.with_lock)
- [panel.io.embed
  module](panel.io.embed.md)
  - [embed_state()](panel.io.embed.md#panel.io.embed.embed_state)
  - [link_to_jslink()](panel.io.embed.md#panel.io.embed.link_to_jslink)
  - [param_to_jslink()](panel.io.embed.md#panel.io.embed.param_to_jslink)
- [panel.io.fastapi module](panel.io.fastapi.md)
- [panel.io.handlers module](panel.io.handlers.md)
  - [FunctionHandler](panel.io.handlers.md#panel.io.handlers.FunctionHandler)
    - [FunctionHandler.modify_document()](panel.io.handlers.md#panel.io.handlers.FunctionHandler.modify_document)
  - [MarkdownHandler](panel.io.handlers.md#panel.io.handlers.MarkdownHandler)
  - [NotebookHandler](panel.io.handlers.md#panel.io.handlers.NotebookHandler)
    - [NotebookHandler.modify_document()](panel.io.handlers.md#panel.io.handlers.NotebookHandler.modify_document)
  - [PanelCodeHandler](panel.io.handlers.md#panel.io.handlers.PanelCodeHandler)
    - [PanelCodeHandler.modify_document()](panel.io.handlers.md#panel.io.handlers.PanelCodeHandler.modify_document)
    - [PanelCodeHandler.url_path()](panel.io.handlers.md#panel.io.handlers.PanelCodeHandler.url_path)
  - [PanelCodeRunner](panel.io.handlers.md#panel.io.handlers.PanelCodeRunner)
    - [PanelCodeRunner.run()](panel.io.handlers.md#panel.io.handlers.PanelCodeRunner.run)
  - [ScriptHandler](panel.io.handlers.md#panel.io.handlers.ScriptHandler)
  - [capture_code_cell()](panel.io.handlers.md#panel.io.handlers.capture_code_cell)
  - [extract_code()](panel.io.handlers.md#panel.io.handlers.extract_code)
  - [parse_notebook()](panel.io.handlers.md#panel.io.handlers.parse_notebook)
- [panel.io.ipywidget module](panel.io.ipywidget.md)
  - [MessageSentBuffers](panel.io.ipywidget.md#panel.io.ipywidget.MessageSentBuffers)
  - [MessageSentEventPatched](panel.io.ipywidget.md#panel.io.ipywidget.MessageSentEventPatched)
  - [PanelKernel](panel.io.ipywidget.md#panel.io.ipywidget.PanelKernel)
  - [PanelSessionWebsocket](panel.io.ipywidget.md#panel.io.ipywidget.PanelSessionWebsocket)
    - [PanelSessionWebsocket.send()](panel.io.ipywidget.md#panel.io.ipywidget.PanelSessionWebsocket.send)
  - [TempComm](panel.io.ipywidget.md#panel.io.ipywidget.TempComm)
- [panel.io.jupyter_executor module](panel.io.jupyter_executor.md)
  - [JupyterServerSession](panel.io.jupyter_executor.md#panel.io.jupyter_executor.JupyterServerSession)
  - [PanelExecutor](panel.io.jupyter_executor.md#panel.io.jupyter_executor.PanelExecutor)
    - [PanelExecutor.render_mime()](panel.io.jupyter_executor.md#panel.io.jupyter_executor.PanelExecutor.render_mime)
    - [PanelExecutor.write_message()](panel.io.jupyter_executor.md#panel.io.jupyter_executor.PanelExecutor.write_message)
- [panel.io.jupyter_server_extension module](panel.io.jupyter_server_extension.md)
  - [PanelBaseHandler](panel.io.jupyter_server_extension.md#panel.io.jupyter_server_extension.PanelBaseHandler)
    - [PanelBaseHandler.initialize()](panel.io.jupyter_server_extension.md#panel.io.jupyter_server_extension.PanelBaseHandler.initialize)
  - [PanelJupyterHandler](panel.io.jupyter_server_extension.md#panel.io.jupyter_server_extension.PanelJupyterHandler)
    - [PanelJupyterHandler.initialize()](panel.io.jupyter_server_extension.md#panel.io.jupyter_server_extension.PanelJupyterHandler.initialize)
  - [PanelLayoutHandler](panel.io.jupyter_server_extension.md#panel.io.jupyter_server_extension.PanelLayoutHandler)
  - [PanelWSProxy](panel.io.jupyter_server_extension.md#panel.io.jupyter_server_extension.PanelWSProxy)
    - [PanelWSProxy.check_origin()](panel.io.jupyter_server_extension.md#panel.io.jupyter_server_extension.PanelWSProxy.check_origin)
    - [PanelWSProxy.get_current_user()](panel.io.jupyter_server_extension.md#panel.io.jupyter_server_extension.PanelWSProxy.get_current_user)
    - [PanelWSProxy.initialize()](panel.io.jupyter_server_extension.md#panel.io.jupyter_server_extension.PanelWSProxy.initialize)
    - [PanelWSProxy.on_close()](panel.io.jupyter_server_extension.md#panel.io.jupyter_server_extension.PanelWSProxy.on_close)
    - [PanelWSProxy.on_message()](panel.io.jupyter_server_extension.md#panel.io.jupyter_server_extension.PanelWSProxy.on_message)
    - [PanelWSProxy.open()](panel.io.jupyter_server_extension.md#panel.io.jupyter_server_extension.PanelWSProxy.open)
    - [PanelWSProxy.prepare()](panel.io.jupyter_server_extension.md#panel.io.jupyter_server_extension.PanelWSProxy.prepare)
  - [ensure_async()](panel.io.jupyter_server_extension.md#panel.io.jupyter_server_extension.ensure_async)
  - [generate_executor()](panel.io.jupyter_server_extension.md#panel.io.jupyter_server_extension.generate_executor)
  - [url_path_join()](panel.io.jupyter_server_extension.md#panel.io.jupyter_server_extension.url_path_join)
- [panel.io.liveness module](panel.io.liveness.md)
  - [LivenessHandler](panel.io.liveness.md#panel.io.liveness.LivenessHandler)
    - [LivenessHandler.initialize()](panel.io.liveness.md#panel.io.liveness.LivenessHandler.initialize)
- [panel.io.loading module](panel.io.loading.md)
  - [start_loading_spinner()](panel.io.loading.md#panel.io.loading.start_loading_spinner)
  - [stop_loading_spinner()](panel.io.loading.md#panel.io.loading.stop_loading_spinner)
- [panel.io.location module](panel.io.location.md)
  - [Location](panel.io.location.md#panel.io.location.Location)
    - [Location.get_root()](panel.io.location.md#panel.io.location.Location.get_root)
    - [Location.sync()](panel.io.location.md#panel.io.location.Location.sync)
    - [Location.unsync()](panel.io.location.md#panel.io.location.Location.unsync)
- [panel.io.logging module](panel.io.logging.md)
- [panel.io.mime_render module](panel.io.mime_render.md)
  - [WriteCallbackStream](panel.io.mime_render.md#panel.io.mime_render.WriteCallbackStream)
    - [WriteCallbackStream.write()](panel.io.mime_render.md#panel.io.mime_render.WriteCallbackStream.write)
  - [eval_formatter()](panel.io.mime_render.md#panel.io.mime_render.eval_formatter)
  - [exec_with_return()](panel.io.mime_render.md#panel.io.mime_render.exec_with_return)
  - [find_requirements()](panel.io.mime_render.md#panel.io.mime_render.find_requirements)
  - [format_mime()](panel.io.mime_render.md#panel.io.mime_render.format_mime)
- [panel.io.model
  module](panel.io.model.md)
  - [add_to_doc()](panel.io.model.md#panel.io.model.add_to_doc)
  - [bokeh_repr()](panel.io.model.md#panel.io.model.bokeh_repr)
  - [comparable_array](panel.io.model.md#panel.io.model.comparable_array)
  - [diff()](panel.io.model.md#panel.io.model.diff)
  - [monkeypatch_events()](panel.io.model.md#panel.io.model.monkeypatch_events)
  - [patch_cds_msg()](panel.io.model.md#panel.io.model.patch_cds_msg)
  - [remove_root()](panel.io.model.md#panel.io.model.remove_root)
- [panel.io.notebook module](panel.io.notebook.md)
  - [JupyterCommJSBinary](panel.io.notebook.md#panel.io.notebook.JupyterCommJSBinary)
    - [JupyterCommJSBinary.decode()](panel.io.notebook.md#panel.io.notebook.JupyterCommJSBinary.decode)
  - [JupyterCommManagerBinary](panel.io.notebook.md#panel.io.notebook.JupyterCommManagerBinary)
    - [JupyterCommManagerBinary.client_comm](panel.io.notebook.md#panel.io.notebook.JupyterCommManagerBinary.client_comm)
  - [Mimebundle](panel.io.notebook.md#panel.io.notebook.Mimebundle)
  - [block_comm()](panel.io.notebook.md#panel.io.notebook.block_comm)
  - [ipywidget()](panel.io.notebook.md#panel.io.notebook.ipywidget)
  - [mime_renderer()](panel.io.notebook.md#panel.io.notebook.mime_renderer)
  - [mimebundle_to_html()](panel.io.notebook.md#panel.io.notebook.mimebundle_to_html)
  - [push()](panel.io.notebook.md#panel.io.notebook.push)
  - [push_notebook()](panel.io.notebook.md#panel.io.notebook.push_notebook)
  - [render_embed()](panel.io.notebook.md#panel.io.notebook.render_embed)
  - [render_mimebundle()](panel.io.notebook.md#panel.io.notebook.render_mimebundle)
  - [require_components()](panel.io.notebook.md#panel.io.notebook.require_components)
  - [send()](panel.io.notebook.md#panel.io.notebook.send)
  - [show_server()](panel.io.notebook.md#panel.io.notebook.show_server)
- [panel.io.notifications module](panel.io.notifications.md)
  - [Notification](panel.io.notifications.md#panel.io.notifications.Notification)
  - [NotificationArea](panel.io.notifications.md#panel.io.notifications.NotificationArea)
    - [NotificationArea.demo()](panel.io.notifications.md#panel.io.notifications.NotificationArea.demo)
    - [NotificationArea.get_root()](panel.io.notifications.md#panel.io.notifications.NotificationArea.get_root)
    - [NotificationArea.send()](panel.io.notifications.md#panel.io.notifications.NotificationArea.send)
  - [NotificationAreaBase](panel.io.notifications.md#panel.io.notifications.NotificationAreaBase)
    - [NotificationAreaBase.send()](panel.io.notifications.md#panel.io.notifications.NotificationAreaBase.send)
- [panel.io.profile module](panel.io.profile.md)
  - [profile()](panel.io.profile.md#panel.io.profile.profile)
  - [profile_ctx()](panel.io.profile.md#panel.io.profile.profile_ctx)
- [panel.io.pyodide module](panel.io.pyodide.md)
- [panel.io.reload module](panel.io.reload.md)
  - [file_is_in_folder_glob()](panel.io.reload.md#panel.io.reload.file_is_in_folder_glob)
  - [record_modules()](panel.io.reload.md#panel.io.reload.record_modules)
  - [setup_autoreload_watcher()](panel.io.reload.md#panel.io.reload.setup_autoreload_watcher)
  - [watch()](panel.io.reload.md#panel.io.reload.watch)
- [panel.io.resources module](panel.io.resources.md)
  - [ResourceComponent](panel.io.resources.md#panel.io.resources.ResourceComponent)
    - [ResourceComponent.resolve_resources()](panel.io.resources.md#panel.io.resources.ResourceComponent.resolve_resources)
  - [Resources](panel.io.resources.md#panel.io.resources.Resources)
    - [Resources.adjust_paths()](panel.io.resources.md#panel.io.resources.Resources.adjust_paths)
    - [Resources.clone()](panel.io.resources.md#panel.io.resources.Resources.clone)
    - [Resources.extra_resources()](panel.io.resources.md#panel.io.resources.Resources.extra_resources)
  - [component_resource_path()](panel.io.resources.md#panel.io.resources.component_resource_path)
  - [get_env()](panel.io.resources.md#panel.io.resources.get_env)
  - [json_dumps](panel.io.resources.md#panel.io.resources.json_dumps)
    - [json_dumps.default()](panel.io.resources.md#panel.io.resources.json_dumps.default)
  - [patch_model_css()](panel.io.resources.md#panel.io.resources.patch_model_css)
  - [process_raw_css()](panel.io.resources.md#panel.io.resources.process_raw_css)
  - [resolve_custom_path()](panel.io.resources.md#panel.io.resources.resolve_custom_path)
  - [resolve_resource_cdn()](panel.io.resources.md#panel.io.resources.resolve_resource_cdn)
  - [resolve_stylesheet()](panel.io.resources.md#panel.io.resources.resolve_stylesheet)
- [panel.io.rest
  module](panel.io.rest.md)
  - [BaseHandler](panel.io.rest.md#panel.io.rest.BaseHandler)
    - [BaseHandler.write_error()](panel.io.rest.md#panel.io.rest.BaseHandler.write_error)
  - [HTTPError](panel.io.rest.md#panel.io.rest.HTTPError)
  - [ParamHandler](panel.io.rest.md#panel.io.rest.ParamHandler)
  - [param_rest_provider()](panel.io.rest.md#panel.io.rest.param_rest_provider)
  - [tranquilizer_rest_provider()](panel.io.rest.md#panel.io.rest.tranquilizer_rest_provider)
- [panel.io.save
  module](panel.io.save.md)
  - [save()](panel.io.save.md#panel.io.save.save)
  - [save_png()](panel.io.save.md#panel.io.save.save_png)
- [panel.io.server module](panel.io.server.md)
  - [AuthenticatedStaticFileHandler](panel.io.server.md#panel.io.server.AuthenticatedStaticFileHandler)
    - [AuthenticatedStaticFileHandler.get_current_user()](panel.io.server.md#panel.io.server.AuthenticatedStaticFileHandler.get_current_user)
    - [AuthenticatedStaticFileHandler.get_login_url()](panel.io.server.md#panel.io.server.AuthenticatedStaticFileHandler.get_login_url)
    - [AuthenticatedStaticFileHandler.prepare()](panel.io.server.md#panel.io.server.AuthenticatedStaticFileHandler.prepare)
  - [AutoloadJsHandler](panel.io.server.md#panel.io.server.AutoloadJsHandler)
  - [ComponentResourceHandler](panel.io.server.md#panel.io.server.ComponentResourceHandler)
    - [ComponentResourceHandler.get_absolute_path()](panel.io.server.md#panel.io.server.ComponentResourceHandler.get_absolute_path)
    - [ComponentResourceHandler.initialize()](panel.io.server.md#panel.io.server.ComponentResourceHandler.initialize)
    - [ComponentResourceHandler.parse_url_path()](panel.io.server.md#panel.io.server.ComponentResourceHandler.parse_url_path)
    - [ComponentResourceHandler.validate_absolute_path()](panel.io.server.md#panel.io.server.ComponentResourceHandler.validate_absolute_path)
  - [DocHandler](panel.io.server.md#panel.io.server.DocHandler)
  - [LoginUrlMixin](panel.io.server.md#panel.io.server.LoginUrlMixin)
    - [LoginUrlMixin.get_login_url()](panel.io.server.md#panel.io.server.LoginUrlMixin.get_login_url)
  - [ProxyFallbackHandler](panel.io.server.md#panel.io.server.ProxyFallbackHandler)
    - [ProxyFallbackHandler.initialize()](panel.io.server.md#panel.io.server.ProxyFallbackHandler.initialize)
    - [ProxyFallbackHandler.prepare()](panel.io.server.md#panel.io.server.ProxyFallbackHandler.prepare)
  - [RootHandler](panel.io.server.md#panel.io.server.RootHandler)
    - [RootHandler.render()](panel.io.server.md#panel.io.server.RootHandler.render)
  - [Server](panel.io.server.md#panel.io.server.Server)
    - [Server.start()](panel.io.server.md#panel.io.server.Server.start)
    - [Server.stop()](panel.io.server.md#panel.io.server.Server.stop)
  - [WSHandler](panel.io.server.md#panel.io.server.WSHandler)
    - [WSHandler.open()](panel.io.server.md#panel.io.server.WSHandler.open)
    - [WSHandler.prepare()](panel.io.server.md#panel.io.server.WSHandler.prepare)
  - [async_execute()](panel.io.server.md#panel.io.server.async_execute)
  - [get_server()](panel.io.server.md#panel.io.server.get_server)
  - [get_static_routes()](panel.io.server.md#panel.io.server.get_static_routes)
  - [html_page_for_render_items()](panel.io.server.md#panel.io.server.html_page_for_render_items)
  - [serve()](panel.io.server.md#panel.io.server.serve)
- [panel.io.session module](panel.io.session.md)
  - [ServerSessionStub](panel.io.session.md#panel.io.session.ServerSessionStub)
- [panel.io.state
  module](panel.io.state.md)
- [panel.io.threads module](panel.io.threads.md)
  - [StoppableThread](panel.io.threads.md#panel.io.threads.StoppableThread)
    - [StoppableThread.run()](panel.io.threads.md#panel.io.threads.StoppableThread.run)

## Module contents

The io module contains utilities for loading JS components, embedding
model state, and rendering panel objects.

class panel.io.PeriodicCallback(\*, callback, count, counter, log, period, running, session_scoped, timeout, name)
Bases: `Parameterized`

Periodic encapsulates a periodic callback which will run both in tornado
based notebook environments and on bokeh server. By default the callback
will run until the stop method is called, but count and timeout values
can be set to limit the number of executions or the maximum length of
time for which the callback will run. The callback may also be started
and stopped by setting the running parameter to True or False
respectively.

Methods

|  |  |
|----|----|
| [start](#panel.io.PeriodicCallback.start)() | Starts running the periodic callback. |
| [stop](#panel.io.PeriodicCallback.stop)() | Stops running the periodic callback. |

**Parameter Definitions**

------------------------------------------------------------------------

`callback`` ``=`` ``Callable(allow_None=True,`` ``label='Callback')`
The callback to execute periodically.

`counter`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Counter')`
Counts the number of executions.

`count`` ``=`` ``Integer(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Count')`
Number of times the callback will be executed, by default this is
unlimited.

`log`` ``=`` ``Boolean(default=True,`` ``label='Log')`
Whether the periodic callback should log its actions.

`period`` ``=`` ``Integer(default=500,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Period')`
Period in milliseconds at which the callback is executed.

`running`` ``=`` ``Boolean(default=False,`` ``label='Running')`
Toggles whether the periodic callback is currently running.

`session_scoped`` ``=`` ``Boolean(default=True,`` ``label='Session`` ``scoped')`
If scheduled from inside a user session scopes the callback to that
session.

`timeout`` ``=`` ``Integer(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Timeout')`
Timeout in milliseconds from the start time at which the callback
expires.

start()
Starts running the periodic callback.

stop()
Stops running the periodic callback.

class panel.io.Resources(\*args, absolute=False, notebook=False, **kwargs)
Bases: `Resources`

adjust_paths(resources)
Computes relative and absolute paths for resources.

clone(\*, components=None) → \[source\]
Make a clone of a resources instance allowing to override its
components.

extra_resources(resources, resource_type)
Adds resources for ReactiveHTML components.

panel.io.hold(doc: Document \| None = None, policy: HoldPolicyType = 'combine', comm: Comm \| None = None, freeze: bool = False)
Context manager that holds events on a particular Document allowing them
all to be collected and dispatched when the context manager exits. This
allows multiple events on the same object to be combined if the policy
is set to ‘combine’.

Parameters:
**doc: Document**
The Bokeh Document to hold events on.

**policy: HoldPolicyType**
One of ‘combine’, ‘collect’ or None determining whether events setting
the same property are combined or accumulated to be dispatched when the
context manager exits.

**comm: Comm**
The Comm to dispatch events on when the context manager exits.

**freeze: bool**
**Experimental.** Whether to freeze the Document model references for
the duration of the hold. When True, defers expensive model graph
recomputation (`doc.models.recompute()`) until
the hold exits, which can significantly speed up batch updates that
modify many models. Safe to nest with the per-model
`freeze_doc` calls used internally, since
Bokeh’s freeze mechanism is reference-counted.

panel.io.immediate_dispatch(doc: Document \| None = None)
Context manager to trigger immediate dispatch of events triggered inside
the execution context even when Document events are currently on hold.

Parameters:
**doc: Document**
The document to dispatch events on (if None then state.curdoc is used).

panel.io.ipywidget(obj: Any, doc=None, **kwargs: Any)
Returns an ipywidget model which renders the Panel object.

Requires jupyter_bokeh to be installed.

Parameters:
**obj: object**
Any Panel object or object which can be rendered with Panel

**doc: bokeh.Document**
Bokeh document the bokeh model will be attached to.

****kwargs: dict**
Keyword arguments passed to the pn.panel utility function

Returns:
Returns an ipywidget model which renders the Panel object.

panel.io.profile(name: str, engine: ProfilingEngine = 'pyinstrument') → Callable\[\[Callable\[\_P, \_R\]\], Callable\[\_P, \_R\]\]
A decorator which may be added to any function to record profiling
output.

Parameters:
**name: str**
A unique name for the profiling session.

**engine: str**
The profiling engine, e.g. ‘pyinstrument’, ‘snakeviz’ or ‘memray’

panel.io.push(doc: Document, comm: Comm, binary: bool = True, msg: Message \| None = None) → None
Pushes events stored on the document across the provided comm.

panel.io.push_notebook(\*objs: Viewable) → None
A utility for pushing updates to the frontend given a Panel object. This
is required when modifying any Bokeh object directly in a notebook
session.

Parameters:
**objs: panel.viewable.Viewable**

panel.io.serve(panels: TViewableFuncOrPath \| dict\[str, TViewableFuncOrPath\], port: int = 0, address: str \| None = None, websocket_origin: str \| list\[str\] \| None = None, loop: IOLoop \| None = None, show: bool = True, start: bool = True, title: str \| None = None, verbose: bool = True, location: bool = True, threaded: bool = False, admin: bool = False, **kwargs) → StoppableThread \| Server
Allows serving one or more panel objects on a single server. The panels
argument should be either a Panel object or a function returning a Panel
object or a dictionary of these two. If a dictionary is supplied the
keys represent the slugs at which each app is served, e.g. serve({‘app’:
panel1, ‘app2’: panel2}) will serve apps at /app and /app2 on the
server.

Reference: [https://panel.holoviz.org/user_guide/Server_Configuration.html#serving-multiple-apps](https://panel.holoviz.org/user_guide/Server_Configuration.html#serving-multiple-apps)

Parameters:
**panels: Viewable, function or {str: Viewable or function}**
A Panel object, a function returning a Panel object or a dictionary
mapping from the URL slug to either.

**port: int (optional, default=0)**
Allows specifying a specific port

address : str
The address the server should listen on for HTTP requests.

**websocket_origin: str or list(str) (optional)**
A list of hosts that can connect to the websocket.

This is typically required when embedding a server app in an external
web site.

If None, “localhost” is used.

loop : tornado.ioloop.IOLoop (optional, default=IOLoop.current())
The tornado IOLoop to run the Server on

show : boolean (optional, default=True)
Whether to open the server in a new browser tab on start

start : boolean(optional, default=True)
Whether to start the Server

**title: str or {str: str} (optional, default=None)**
An HTML title for the application or a dictionary mapping from the URL
slug to a customized title

**verbose: boolean (optional, default=True)**
Whether to print the address and port

location : boolean or panel.io.location.Location
Whether to create a Location component to observe and set the URL
location.

**threaded: boolean (default=False)**
Whether to start the server on a new Thread

**admin: boolean (default=False)**
Whether to enable the admin panel

**kwargs: dict**
Additional keyword arguments to pass to Server instance

panel.io.unlocked(policy: HoldPolicyType = 'combine') → Iterator
Context manager which unlocks a Document and dispatches
ModelChangedEvents triggered in the context body to all sockets on
current sessions.

Parameters:
**policy: Literal\[‘combine’ \| ‘collect’\]**
One of ‘combine’ or ‘collect’ determining whether events setting the
same property are combined or accumulated to be dispatched when the
context manager exits.

panel.io.with_lock(func: Callable) → Callable
Wrap a callback function to execute with a lock allowing the function to
modify bokeh models directly.

Parameters:
**func: callable**
The callable to wrap

Returns:
wrapper: callable
Function wrapped to execute without a Document lock.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
