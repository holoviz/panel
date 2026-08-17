# panel package

## Subpackages

- [panel.chat
  package](panel.chat.md)
  - [Submodules](panel.chat.md#submodules)
    - [panel.chat.feed module](panel.chat.feed.md)
      - [CallbackState](panel.chat.feed.md#panel.chat.feed.CallbackState)
      - [ChatFeed](panel.chat.feed.md#panel.chat.feed.ChatFeed)
      - [StopCallback](panel.chat.feed.md#panel.chat.feed.StopCallback)
    - [panel.chat.icon module](panel.chat.icon.md)
      - [ChatCopyIcon](panel.chat.icon.md#panel.chat.icon.ChatCopyIcon)
      - [ChatReactionIcons](panel.chat.icon.md#panel.chat.icon.ChatReactionIcons)
    - [panel.chat.input module](panel.chat.input.md)
      - [ChatAreaInput](panel.chat.input.md#panel.chat.input.ChatAreaInput)
    - [panel.chat.interface module](panel.chat.interface.md)
      - [ChatInterface](panel.chat.interface.md#panel.chat.interface.ChatInterface)
    - [panel.chat.langchain module](panel.chat.langchain.md)
      - [PanelCallbackHandler](panel.chat.langchain.md#panel.chat.langchain.PanelCallbackHandler)
    - [panel.chat.message module](panel.chat.message.md)
      - [ChatMessage](panel.chat.message.md#panel.chat.message.ChatMessage)
    - [panel.chat.step module](panel.chat.step.md)
      - [ChatStep](panel.chat.step.md#panel.chat.step.ChatStep)
    - [panel.chat.utils module](panel.chat.utils.md)
      - [avatar_lookup()](panel.chat.utils.md#panel.chat.utils.avatar_lookup)
      - [get_obj_label()](panel.chat.utils.md#panel.chat.utils.get_obj_label)
      - [serialize_recursively()](panel.chat.utils.md#panel.chat.utils.serialize_recursively)
      - [stream_to()](panel.chat.utils.md#panel.chat.utils.stream_to)
      - [to_alpha_numeric()](panel.chat.utils.md#panel.chat.utils.to_alpha_numeric)
  - [Module contents](panel.chat.md#module-panel.chat)
    - [Panel chat makes creating chat components
      easy](panel.chat.md#panel-chat-makes-creating-chat-components-easy)
      - [How to use Panel widgets in 3 simple
        steps](panel.chat.md#how-to-use-panel-widgets-in-3-simple-steps)
    - [ChatAreaInput](panel.chat.md#panel.chat.ChatAreaInput)
    - [ChatFeed](panel.chat.md#panel.chat.ChatFeed)
      - [ChatFeed.add_step()](panel.chat.md#panel.chat.ChatFeed.add_step)
      - [ChatFeed.clear()](panel.chat.md#panel.chat.ChatFeed.clear)
      - [ChatFeed.prompt_user()](panel.chat.md#panel.chat.ChatFeed.prompt_user)
      - [ChatFeed.respond()](panel.chat.md#panel.chat.ChatFeed.respond)
      - [ChatFeed.scroll_to()](panel.chat.md#panel.chat.ChatFeed.scroll_to)
      - [ChatFeed.select()](panel.chat.md#panel.chat.ChatFeed.select)
      - [ChatFeed.send()](panel.chat.md#panel.chat.ChatFeed.send)
      - [ChatFeed.serialize()](panel.chat.md#panel.chat.ChatFeed.serialize)
      - [ChatFeed.stop()](panel.chat.md#panel.chat.ChatFeed.stop)
      - [ChatFeed.stream()](panel.chat.md#panel.chat.ChatFeed.stream)
      - [ChatFeed.trigger_post_hook()](panel.chat.md#panel.chat.ChatFeed.trigger_post_hook)
      - [ChatFeed.undo()](panel.chat.md#panel.chat.ChatFeed.undo)
    - [ChatInterface](panel.chat.md#panel.chat.ChatInterface)
      - [ChatInterface.active](panel.chat.md#panel.chat.ChatInterface.active)
      - [ChatInterface.active_widget](panel.chat.md#panel.chat.ChatInterface.active_widget)
      - [ChatInterface.send()](panel.chat.md#panel.chat.ChatInterface.send)
      - [ChatInterface.stream()](panel.chat.md#panel.chat.ChatInterface.stream)
    - [ChatMessage](panel.chat.md#panel.chat.ChatMessage)
      - [ChatMessage.select()](panel.chat.md#panel.chat.ChatMessage.select)
      - [ChatMessage.serialize()](panel.chat.md#panel.chat.ChatMessage.serialize)
      - [ChatMessage.stream()](panel.chat.md#panel.chat.ChatMessage.stream)
      - [ChatMessage.update()](panel.chat.md#panel.chat.ChatMessage.update)
    - [ChatReactionIcons](panel.chat.md#panel.chat.ChatReactionIcons)
      - [ChatReactionIcons.default_layout](panel.chat.md#panel.chat.ChatReactionIcons.default_layout)
    - [ChatStep](panel.chat.md#panel.chat.ChatStep)
      - [ChatStep.serialize()](panel.chat.md#panel.chat.ChatStep.serialize)
      - [ChatStep.stream()](panel.chat.md#panel.chat.ChatStep.stream)
      - [ChatStep.stream_title()](panel.chat.md#panel.chat.ChatStep.stream_title)
- [panel.command
  package](panel.command.md)
  - [Submodules](panel.command.md#submodules)
    - [panel.command.bundle module](panel.command.bundle.md)
      - [Bundle](panel.command.bundle.md#panel.command.bundle.Bundle)
    - [panel.command.compile module](panel.command.compile.md)
      - [Compile](panel.command.compile.md#panel.command.compile.Compile)
      - [run_compile()](panel.command.compile.md#panel.command.compile.run_compile)
    - [panel.command.convert module](panel.command.convert.md)
      - [Convert](panel.command.convert.md#panel.command.convert.Convert)
    - [panel.command.oauth_secret module](panel.command.oauth_secret.md)
      - [OAuthSecret](panel.command.oauth_secret.md#panel.command.oauth_secret.OAuthSecret)
    - [panel.command.serve module](panel.command.serve.md)
      - [AdminApplicationContext](panel.command.serve.md#panel.command.serve.AdminApplicationContext)
      - [Serve](panel.command.serve.md#panel.command.serve.Serve)
      - [add_sys_path()](panel.command.serve.md#panel.command.serve.add_sys_path)
      - [parse_var()](panel.command.serve.md#panel.command.serve.parse_var)
      - [parse_vars()](panel.command.serve.md#panel.command.serve.parse_vars)
  - [Module contents](panel.command.md#module-panel.command)
    - [transform_cmds()](panel.command.md#panel.command.transform_cmds)
- [panel.io package](panel.io.md)
  - [Submodules](panel.io.md#submodules)
    - [panel.io.admin
      module](panel.io.admin.md)
      - [Data](panel.io.admin.md#panel.io.admin.Data)
      - [LogDataHandler](panel.io.admin.md#panel.io.admin.LogDataHandler)
      - [LogFilter](panel.io.admin.md#panel.io.admin.LogFilter)
    - [panel.io.application module](panel.io.application.md)
      - [Application](panel.io.application.md#panel.io.application.Application)
      - [build_applications()](panel.io.application.md#panel.io.application.build_applications)
    - [panel.io.browser module](panel.io.browser.md)
      - [BrowserInfo](panel.io.browser.md#panel.io.browser.BrowserInfo)
    - [panel.io.cache
      module](panel.io.cache.md)
      - [cache()](panel.io.cache.md#panel.io.cache.cache)
      - [compute_hash()](panel.io.cache.md#panel.io.cache.compute_hash)
      - [is_equal()](panel.io.cache.md#panel.io.cache.is_equal)
    - [panel.io.callbacks module](panel.io.callbacks.md)
      - [PeriodicCallback](panel.io.callbacks.md#panel.io.callbacks.PeriodicCallback)
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
      - [PolarsDataFrame](panel.io.datamodel.md#panel.io.datamodel.PolarsDataFrame)
      - [construct_data_model()](panel.io.datamodel.md#panel.io.datamodel.construct_data_model)
      - [create_linked_datamodel()](panel.io.datamodel.md#panel.io.datamodel.create_linked_datamodel)
    - [panel.io.django module](panel.io.django.md)
    - [panel.io.document module](panel.io.document.md)
      - [MockSessionContext](panel.io.document.md#panel.io.document.MockSessionContext)
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
      - [MarkdownHandler](panel.io.handlers.md#panel.io.handlers.MarkdownHandler)
      - [NotebookHandler](panel.io.handlers.md#panel.io.handlers.NotebookHandler)
      - [PanelCodeHandler](panel.io.handlers.md#panel.io.handlers.PanelCodeHandler)
      - [PanelCodeRunner](panel.io.handlers.md#panel.io.handlers.PanelCodeRunner)
      - [ScriptHandler](panel.io.handlers.md#panel.io.handlers.ScriptHandler)
      - [capture_code_cell()](panel.io.handlers.md#panel.io.handlers.capture_code_cell)
      - [extract_code()](panel.io.handlers.md#panel.io.handlers.extract_code)
      - [parse_notebook()](panel.io.handlers.md#panel.io.handlers.parse_notebook)
    - [panel.io.ipywidget module](panel.io.ipywidget.md)
      - [MessageSentBuffers](panel.io.ipywidget.md#panel.io.ipywidget.MessageSentBuffers)
      - [MessageSentEventPatched](panel.io.ipywidget.md#panel.io.ipywidget.MessageSentEventPatched)
      - [PanelKernel](panel.io.ipywidget.md#panel.io.ipywidget.PanelKernel)
      - [PanelSessionWebsocket](panel.io.ipywidget.md#panel.io.ipywidget.PanelSessionWebsocket)
      - [TempComm](panel.io.ipywidget.md#panel.io.ipywidget.TempComm)
    - [panel.io.jupyter_executor module](panel.io.jupyter_executor.md)
      - [JupyterServerSession](panel.io.jupyter_executor.md#panel.io.jupyter_executor.JupyterServerSession)
      - [PanelExecutor](panel.io.jupyter_executor.md#panel.io.jupyter_executor.PanelExecutor)
    - [panel.io.jupyter_server_extension module](panel.io.jupyter_server_extension.md)
      - [PanelBaseHandler](panel.io.jupyter_server_extension.md#panel.io.jupyter_server_extension.PanelBaseHandler)
      - [PanelJupyterHandler](panel.io.jupyter_server_extension.md#panel.io.jupyter_server_extension.PanelJupyterHandler)
      - [PanelLayoutHandler](panel.io.jupyter_server_extension.md#panel.io.jupyter_server_extension.PanelLayoutHandler)
      - [PanelWSProxy](panel.io.jupyter_server_extension.md#panel.io.jupyter_server_extension.PanelWSProxy)
      - [ensure_async()](panel.io.jupyter_server_extension.md#panel.io.jupyter_server_extension.ensure_async)
      - [generate_executor()](panel.io.jupyter_server_extension.md#panel.io.jupyter_server_extension.generate_executor)
      - [url_path_join()](panel.io.jupyter_server_extension.md#panel.io.jupyter_server_extension.url_path_join)
    - [panel.io.liveness module](panel.io.liveness.md)
      - [LivenessHandler](panel.io.liveness.md#panel.io.liveness.LivenessHandler)
    - [panel.io.loading module](panel.io.loading.md)
      - [start_loading_spinner()](panel.io.loading.md#panel.io.loading.start_loading_spinner)
      - [stop_loading_spinner()](panel.io.loading.md#panel.io.loading.stop_loading_spinner)
    - [panel.io.location module](panel.io.location.md)
      - [Location](panel.io.location.md#panel.io.location.Location)
    - [panel.io.logging module](panel.io.logging.md)
    - [panel.io.mime_render module](panel.io.mime_render.md)
      - [WriteCallbackStream](panel.io.mime_render.md#panel.io.mime_render.WriteCallbackStream)
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
      - [JupyterCommManagerBinary](panel.io.notebook.md#panel.io.notebook.JupyterCommManagerBinary)
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
      - [NotificationAreaBase](panel.io.notifications.md#panel.io.notifications.NotificationAreaBase)
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
      - [Resources](panel.io.resources.md#panel.io.resources.Resources)
      - [component_resource_path()](panel.io.resources.md#panel.io.resources.component_resource_path)
      - [get_env()](panel.io.resources.md#panel.io.resources.get_env)
      - [json_dumps](panel.io.resources.md#panel.io.resources.json_dumps)
      - [patch_model_css()](panel.io.resources.md#panel.io.resources.patch_model_css)
      - [process_raw_css()](panel.io.resources.md#panel.io.resources.process_raw_css)
      - [resolve_custom_path()](panel.io.resources.md#panel.io.resources.resolve_custom_path)
      - [resolve_resource_cdn()](panel.io.resources.md#panel.io.resources.resolve_resource_cdn)
      - [resolve_stylesheet()](panel.io.resources.md#panel.io.resources.resolve_stylesheet)
    - [panel.io.rest
      module](panel.io.rest.md)
      - [BaseHandler](panel.io.rest.md#panel.io.rest.BaseHandler)
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
      - [AutoloadJsHandler](panel.io.server.md#panel.io.server.AutoloadJsHandler)
      - [ComponentResourceHandler](panel.io.server.md#panel.io.server.ComponentResourceHandler)
      - [DocHandler](panel.io.server.md#panel.io.server.DocHandler)
      - [LoginUrlMixin](panel.io.server.md#panel.io.server.LoginUrlMixin)
      - [ProxyFallbackHandler](panel.io.server.md#panel.io.server.ProxyFallbackHandler)
      - [RootHandler](panel.io.server.md#panel.io.server.RootHandler)
      - [Server](panel.io.server.md#panel.io.server.Server)
      - [WSHandler](panel.io.server.md#panel.io.server.WSHandler)
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
  - [Module contents](panel.io.md#module-panel.io)
    - [PeriodicCallback](panel.io.md#panel.io.PeriodicCallback)
      - [PeriodicCallback.start()](panel.io.md#panel.io.PeriodicCallback.start)
      - [PeriodicCallback.stop()](panel.io.md#panel.io.PeriodicCallback.stop)
    - [Resources](panel.io.md#panel.io.Resources)
      - [Resources.adjust_paths()](panel.io.md#panel.io.Resources.adjust_paths)
      - [Resources.clone()](panel.io.md#panel.io.Resources.clone)
      - [Resources.extra_resources()](panel.io.md#panel.io.Resources.extra_resources)
    - [hold()](panel.io.md#panel.io.hold)
    - [immediate_dispatch()](panel.io.md#panel.io.immediate_dispatch)
    - [ipywidget()](panel.io.md#panel.io.ipywidget)
    - [profile()](panel.io.md#panel.io.profile)
    - [push()](panel.io.md#panel.io.push)
    - [push_notebook()](panel.io.md#panel.io.push_notebook)
    - [serve()](panel.io.md#panel.io.serve)
    - [unlocked()](panel.io.md#panel.io.unlocked)
    - [with_lock()](panel.io.md#panel.io.with_lock)
- [panel.layout
  package](panel.layout.md)
  - [Submodules](panel.layout.md#submodules)
    - [panel.layout.accordion module](panel.layout.accordion.md)
      - [Accordion](panel.layout.accordion.md#panel.layout.accordion.Accordion)
    - [panel.layout.base module](panel.layout.base.md)
      - [Column](panel.layout.base.md#panel.layout.base.Column)
      - [ListLike](panel.layout.base.md#panel.layout.base.ListLike)
      - [ListPanel](panel.layout.base.md#panel.layout.base.ListPanel)
      - [NamedListLike](panel.layout.base.md#panel.layout.base.NamedListLike)
      - [NamedListPanel](panel.layout.base.md#panel.layout.base.NamedListPanel)
      - [Panel](panel.layout.base.md#panel.layout.base.Panel)
      - [Row](panel.layout.base.md#panel.layout.base.Row)
      - [SizingModeMixin](panel.layout.base.md#panel.layout.base.SizingModeMixin)
      - [WidgetBox](panel.layout.base.md#panel.layout.base.WidgetBox)
    - [panel.layout.card module](panel.layout.card.md)
      - [Card](panel.layout.card.md#panel.layout.card.Card)
    - [panel.layout.feed module](panel.layout.feed.md)
      - [Feed](panel.layout.feed.md#panel.layout.feed.Feed)
    - [panel.layout.flex module](panel.layout.flex.md)
      - [FlexBox](panel.layout.flex.md#panel.layout.flex.FlexBox)
    - [panel.layout.float module](panel.layout.float.md)
      - [FloatPanel](panel.layout.float.md#panel.layout.float.FloatPanel)
    - [panel.layout.grid module](panel.layout.grid.md)
      - [GridBox](panel.layout.grid.md#panel.layout.grid.GridBox)
      - [GridSpec](panel.layout.grid.md#panel.layout.grid.GridSpec)
    - [panel.layout.gridstack module](panel.layout.gridstack.md)
      - [GridStack](panel.layout.gridstack.md#panel.layout.gridstack.GridStack)
    - [panel.layout.modal module](panel.layout.modal.md)
      - [Modal](panel.layout.modal.md#panel.layout.modal.Modal)
    - [panel.layout.spacer module](panel.layout.spacer.md)
      - [Divider](panel.layout.spacer.md#panel.layout.spacer.Divider)
      - [HSpacer](panel.layout.spacer.md#panel.layout.spacer.HSpacer)
      - [Spacer](panel.layout.spacer.md#panel.layout.spacer.Spacer)
      - [VSpacer](panel.layout.spacer.md#panel.layout.spacer.VSpacer)
    - [panel.layout.swipe module](panel.layout.swipe.md)
      - [Swipe](panel.layout.swipe.md#panel.layout.swipe.Swipe)
    - [panel.layout.tabs module](panel.layout.tabs.md)
      - [Tabs](panel.layout.tabs.md#panel.layout.tabs.Tabs)
  - [Module contents](panel.layout.md#module-panel.layout)
    - [Layout](panel.layout.md#layout)
      - [How to use layouts in 2 simple steps](panel.layout.md#how-to-use-layouts-in-2-simple-steps)
    - [Accordion](panel.layout.md#panel.layout.Accordion)
      - [Accordion.select()](panel.layout.md#panel.layout.Accordion.select)
    - [Card](panel.layout.md#panel.layout.Card)
      - [Card.select()](panel.layout.md#panel.layout.Card.select)
    - [Column](panel.layout.md#panel.layout.Column)
      - [Column.scroll_to()](panel.layout.md#panel.layout.Column.scroll_to)
    - [Divider](panel.layout.md#panel.layout.Divider)
    - [Feed](panel.layout.md#panel.layout.Feed)
      - [Feed.scroll_to_latest()](panel.layout.md#panel.layout.Feed.scroll_to_latest)
    - [FlexBox](panel.layout.md#panel.layout.FlexBox)
      - [FlexBox.clone()](panel.layout.md#panel.layout.FlexBox.clone)
      - [FlexBox.select()](panel.layout.md#panel.layout.FlexBox.select)
    - [FloatPanel](panel.layout.md#panel.layout.FloatPanel)
      - [FloatPanel.clone()](panel.layout.md#panel.layout.FloatPanel.clone)
      - [FloatPanel.select()](panel.layout.md#panel.layout.FloatPanel.select)
    - [GridBox](panel.layout.md#panel.layout.GridBox)
    - [GridSpec](panel.layout.md#panel.layout.GridSpec)
      - [GridSpec.clone()](panel.layout.md#panel.layout.GridSpec.clone)
    - [GridStack](panel.layout.md#panel.layout.GridStack)
    - [HSpacer](panel.layout.md#panel.layout.HSpacer)
    - [ListLike](panel.layout.md#panel.layout.ListLike)
      - [ListLike.append()](panel.layout.md#panel.layout.ListLike.append)
      - [ListLike.clear()](panel.layout.md#panel.layout.ListLike.clear)
      - [ListLike.clone()](panel.layout.md#panel.layout.ListLike.clone)
      - [ListLike.extend()](panel.layout.md#panel.layout.ListLike.extend)
      - [ListLike.index()](panel.layout.md#panel.layout.ListLike.index)
      - [ListLike.insert()](panel.layout.md#panel.layout.ListLike.insert)
      - [ListLike.pop()](panel.layout.md#panel.layout.ListLike.pop)
      - [ListLike.remove()](panel.layout.md#panel.layout.ListLike.remove)
      - [ListLike.reverse()](panel.layout.md#panel.layout.ListLike.reverse)
    - [ListPanel](panel.layout.md#panel.layout.ListPanel)
      - [ListPanel.clone()](panel.layout.md#panel.layout.ListPanel.clone)
    - [Modal](panel.layout.md#panel.layout.Modal)
      - [Modal.create_button()](panel.layout.md#panel.layout.Modal.create_button)
      - [Modal.show()](panel.layout.md#panel.layout.Modal.show)
    - [Panel](panel.layout.md#panel.layout.Panel)
      - [Panel.get_root()](panel.layout.md#panel.layout.Panel.get_root)
      - [Panel.select()](panel.layout.md#panel.layout.Panel.select)
    - [Row](panel.layout.md#panel.layout.Row)
    - [Spacer](panel.layout.md#panel.layout.Spacer)
    - [Swipe](panel.layout.md#panel.layout.Swipe)
      - [Swipe.clone()](panel.layout.md#panel.layout.Swipe.clone)
      - [Swipe.select()](panel.layout.md#panel.layout.Swipe.select)
    - [Tabs](panel.layout.md#panel.layout.Tabs)
    - [VSpacer](panel.layout.md#panel.layout.VSpacer)
    - [WidgetBox](panel.layout.md#panel.layout.WidgetBox)
- [panel.models
  package](panel.models.md)
  - [Submodules](panel.models.md#submodules)
    - [panel.models.ace module](panel.models.ace.md)
      - [AcePlot](panel.models.ace.md#panel.models.ace.AcePlot)
    - [panel.models.browser module](panel.models.browser.md)
      - [BrowserInfo](panel.models.browser.md#panel.models.browser.BrowserInfo)
    - [panel.models.chatarea_input module](panel.models.chatarea_input.md)
      - [ChatAreaInput](panel.models.chatarea_input.md#panel.models.chatarea_input.ChatAreaInput)
      - [ChatMessageEvent](panel.models.chatarea_input.md#panel.models.chatarea_input.ChatMessageEvent)
    - [panel.models.comm_manager module](panel.models.comm_manager.md)
      - [CommManager](panel.models.comm_manager.md#panel.models.comm_manager.CommManager)
    - [panel.models.datetime_picker module](panel.models.datetime_picker.md)
      - [DatetimePicker](panel.models.datetime_picker.md#panel.models.datetime_picker.DatetimePicker)
    - [panel.models.datetime_slider module](panel.models.datetime_slider.md)
      - [DatetimeSlider](panel.models.datetime_slider.md#panel.models.datetime_slider.DatetimeSlider)
    - [panel.models.deckgl module](panel.models.deckgl.md)
      - [DeckGLPlot](panel.models.deckgl.md#panel.models.deckgl.DeckGLPlot)
    - [panel.models.echarts module](panel.models.echarts.md)
      - [ECharts](panel.models.echarts.md#panel.models.echarts.ECharts)
      - [EChartsEvent](panel.models.echarts.md#panel.models.echarts.EChartsEvent)
    - [panel.models.enums module](panel.models.enums.md)
    - [panel.models.esm module](panel.models.esm.md)
      - [AnyWidgetComponent](panel.models.esm.md#panel.models.esm.AnyWidgetComponent)
      - [DataEvent](panel.models.esm.md#panel.models.esm.DataEvent)
      - [ESMEvent](panel.models.esm.md#panel.models.esm.ESMEvent)
      - [ReactComponent](panel.models.esm.md#panel.models.esm.ReactComponent)
    - [panel.models.feed module](panel.models.feed.md)
      - [Feed](panel.models.feed.md#panel.models.feed.Feed)
      - [ScrollButtonClick](panel.models.feed.md#panel.models.feed.ScrollButtonClick)
      - [ScrollLatestEvent](panel.models.feed.md#panel.models.feed.ScrollLatestEvent)
    - [panel.models.file_dropper module](panel.models.file_dropper.md)
      - [DeleteEvent](panel.models.file_dropper.md#panel.models.file_dropper.DeleteEvent)
      - [FileDropper](panel.models.file_dropper.md#panel.models.file_dropper.FileDropper)
      - [UploadEvent](panel.models.file_dropper.md#panel.models.file_dropper.UploadEvent)
    - [panel.models.icon module](panel.models.icon.md)
      - [ButtonIcon](panel.models.icon.md#panel.models.icon.ButtonIcon)
      - [ToggleIcon](panel.models.icon.md#panel.models.icon.ToggleIcon)
    - [panel.models.ipywidget module](panel.models.ipywidget.md)
    - [panel.models.jsoneditor module](panel.models.jsoneditor.md)
      - [JSONEditEvent](panel.models.jsoneditor.md#panel.models.jsoneditor.JSONEditEvent)
      - [JSONEditor](panel.models.jsoneditor.md#panel.models.jsoneditor.JSONEditor)
    - [panel.models.katex module](panel.models.katex.md)
      - [KaTeX](panel.models.katex.md#panel.models.katex.KaTeX)
    - [panel.models.layout module](panel.models.layout.md)
      - [Card](panel.models.layout.md#panel.models.layout.Card)
      - [Column](panel.models.layout.md#panel.models.layout.Column)
    - [panel.models.location module](panel.models.location.md)
      - [Location](panel.models.location.md#panel.models.location.Location)
    - [panel.models.markup module](panel.models.markup.md)
      - [HTML](panel.models.markup.md#panel.models.markup.HTML)
      - [HTMLStreamEvent](panel.models.markup.md#panel.models.markup.HTMLStreamEvent)
      - [JSON](panel.models.markup.md#panel.models.markup.JSON)
      - [PDF](panel.models.markup.md#panel.models.markup.PDF)
    - [panel.models.mathjax module](panel.models.mathjax.md)
      - [MathJax](panel.models.mathjax.md#panel.models.mathjax.MathJax)
    - [panel.models.modal module](panel.models.modal.md)
      - [Modal](panel.models.modal.md#panel.models.modal.Modal)
      - [ModalDialogEvent](panel.models.modal.md#panel.models.modal.ModalDialogEvent)
    - [panel.models.perspective module](panel.models.perspective.md)
      - [PerspectiveClickEvent](panel.models.perspective.md#panel.models.perspective.PerspectiveClickEvent)
    - [panel.models.plotly module](panel.models.plotly.md)
      - [PlotlyEvent](panel.models.plotly.md#panel.models.plotly.PlotlyEvent)
      - [PlotlyPlot](panel.models.plotly.md#panel.models.plotly.PlotlyPlot)
    - [panel.models.quill module](panel.models.quill.md)
      - [QuillInput](panel.models.quill.md#panel.models.quill.QuillInput)
    - [panel.models.reactive_html module](panel.models.reactive_html.md)
      - [DOMEvent](panel.models.reactive_html.md#panel.models.reactive_html.DOMEvent)
      - [ReactiveHTMLParser](panel.models.reactive_html.md#panel.models.reactive_html.ReactiveHTMLParser)
    - [panel.models.speech_to_text module](panel.models.speech_to_text.md)
      - [SpeechToText](panel.models.speech_to_text.md#panel.models.speech_to_text.SpeechToText)
    - [panel.models.state module](panel.models.state.md)
      - [State](panel.models.state.md#panel.models.state.State)
    - [panel.models.tabs module](panel.models.tabs.md)
      - [Tabs](panel.models.tabs.md#panel.models.tabs.Tabs)
    - [panel.models.tabulator module](panel.models.tabulator.md)
      - [CellClickEvent](panel.models.tabulator.md#panel.models.tabulator.CellClickEvent)
      - [DataTabulator](panel.models.tabulator.md#panel.models.tabulator.DataTabulator)
      - [SelectionEvent](panel.models.tabulator.md#panel.models.tabulator.SelectionEvent)
      - [TableEditEvent](panel.models.tabulator.md#panel.models.tabulator.TableEditEvent)
    - [panel.models.terminal module](panel.models.terminal.md)
      - [KeystrokeEvent](panel.models.terminal.md#panel.models.terminal.KeystrokeEvent)
      - [Terminal](panel.models.terminal.md#panel.models.terminal.Terminal)
    - [panel.models.text_to_speech module](panel.models.text_to_speech.md)
      - [TextToSpeech](panel.models.text_to_speech.md#panel.models.text_to_speech.TextToSpeech)
    - [panel.models.time_picker module](panel.models.time_picker.md)
      - [TimePicker](panel.models.time_picker.md#panel.models.time_picker.TimePicker)
    - [panel.models.trend module](panel.models.trend.md)
      - [TrendIndicator](panel.models.trend.md#panel.models.trend.TrendIndicator)
    - [panel.models.vega module](panel.models.vega.md)
      - [VegaEvent](panel.models.vega.md#panel.models.vega.VegaEvent)
      - [VegaPlot](panel.models.vega.md#panel.models.vega.VegaPlot)
    - [panel.models.vizzu module](panel.models.vizzu.md)
      - [VizzuChart](panel.models.vizzu.md#panel.models.vizzu.VizzuChart)
      - [VizzuEvent](panel.models.vizzu.md#panel.models.vizzu.VizzuEvent)
    - [panel.models.vtk module](panel.models.vtk.md)
      - [AbstractVTKPlot](panel.models.vtk.md#panel.models.vtk.AbstractVTKPlot)
      - [VTKAxes](panel.models.vtk.md#panel.models.vtk.VTKAxes)
      - [VTKJSPlot](panel.models.vtk.md#panel.models.vtk.VTKJSPlot)
      - [VTKSynchronizedPlot](panel.models.vtk.md#panel.models.vtk.VTKSynchronizedPlot)
      - [VTKVolumePlot](panel.models.vtk.md#panel.models.vtk.VTKVolumePlot)
    - [panel.models.widgets module](panel.models.widgets.md)
      - [Button](panel.models.widgets.md#panel.models.widgets.Button)
      - [CheckboxButtonGroup](panel.models.widgets.md#panel.models.widgets.CheckboxButtonGroup)
      - [CustomMultiSelect](panel.models.widgets.md#panel.models.widgets.CustomMultiSelect)
      - [CustomSelect](panel.models.widgets.md#panel.models.widgets.CustomSelect)
      - [DiscretePlayer](panel.models.widgets.md#panel.models.widgets.DiscretePlayer)
      - [DoubleClickEvent](panel.models.widgets.md#panel.models.widgets.DoubleClickEvent)
      - [EnterEvent](panel.models.widgets.md#panel.models.widgets.EnterEvent)
      - [FileDownload](panel.models.widgets.md#panel.models.widgets.FileDownload)
      - [Player](panel.models.widgets.md#panel.models.widgets.Player)
      - [RadioButtonGroup](panel.models.widgets.md#panel.models.widgets.RadioButtonGroup)
      - [SingleSelect](panel.models.widgets.md#panel.models.widgets.SingleSelect)
      - [TextAreaInput](panel.models.widgets.md#panel.models.widgets.TextAreaInput)
      - [TextInput](panel.models.widgets.md#panel.models.widgets.TextInput)
      - [TooltipIcon](panel.models.widgets.md#panel.models.widgets.TooltipIcon)
  - [Module contents](panel.models.md#module-panel.models)
- [panel.pane
  package](panel.pane.md)
  - [Subpackages](panel.pane.md#subpackages)
    - [panel.pane.vtk
      package](panel.pane.vtk.md)
      - [Submodules](panel.pane.vtk.md#submodules)
      - [Module contents](panel.pane.vtk.md#module-panel.pane.vtk)
  - [Submodules](panel.pane.md#submodules)
    - [panel.pane.alert module](panel.pane.alert.md)
      - [Alert](panel.pane.alert.md#panel.pane.alert.Alert)
    - [panel.pane.base module](panel.pane.base.md)
      - [ModelPane](panel.pane.base.md#panel.pane.base.ModelPane)
      - [Pane](panel.pane.base.md#panel.pane.base.Pane)
      - [PaneBase](panel.pane.base.md#panel.pane.base.PaneBase)
      - [ReplacementPane](panel.pane.base.md#panel.pane.base.ReplacementPane)
      - [RerenderError](panel.pane.base.md#panel.pane.base.RerenderError)
      - [panel()](panel.pane.base.md#panel.pane.base.panel)
    - [panel.pane.deckgl module](panel.pane.deckgl.md)
      - [DeckGL](panel.pane.deckgl.md#panel.pane.deckgl.DeckGL)
      - [lower_camel_case_keys()](panel.pane.deckgl.md#panel.pane.deckgl.lower_camel_case_keys)
      - [to_camel_case()](panel.pane.deckgl.md#panel.pane.deckgl.to_camel_case)
    - [panel.pane.echarts module](panel.pane.echarts.md)
      - [ECharts](panel.pane.echarts.md#panel.pane.echarts.ECharts)
    - [panel.pane.equation module](panel.pane.equation.md)
      - [LaTeX](panel.pane.equation.md#panel.pane.equation.LaTeX)
    - [panel.pane.holoviews module](panel.pane.holoviews.md)
      - [HoloViews](panel.pane.holoviews.md#panel.pane.holoviews.HoloViews)
      - [Interactive](panel.pane.holoviews.md#panel.pane.holoviews.Interactive)
      - [find_links()](panel.pane.holoviews.md#panel.pane.holoviews.find_links)
      - [generate_panel_bokeh_map()](panel.pane.holoviews.md#panel.pane.holoviews.generate_panel_bokeh_map)
      - [is_bokeh_element_plot()](panel.pane.holoviews.md#panel.pane.holoviews.is_bokeh_element_plot)
      - [link_axes()](panel.pane.holoviews.md#panel.pane.holoviews.link_axes)
    - [panel.pane.image module](panel.pane.image.md)
      - [AVIF](panel.pane.image.md#panel.pane.image.AVIF)
      - [FileBase](panel.pane.image.md#panel.pane.image.FileBase)
      - [GIF](panel.pane.image.md#panel.pane.image.GIF)
      - [ICO](panel.pane.image.md#panel.pane.image.ICO)
      - [Image](panel.pane.image.md#panel.pane.image.Image)
      - [ImageBase](panel.pane.image.md#panel.pane.image.ImageBase)
      - [JPG](panel.pane.image.md#panel.pane.image.JPG)
      - [PDF](panel.pane.image.md#panel.pane.image.PDF)
      - [PNG](panel.pane.image.md#panel.pane.image.PNG)
      - [SVG](panel.pane.image.md#panel.pane.image.SVG)
      - [WebP](panel.pane.image.md#panel.pane.image.WebP)
    - [panel.pane.ipywidget module](panel.pane.ipywidget.md)
      - [IPyLeaflet](panel.pane.ipywidget.md#panel.pane.ipywidget.IPyLeaflet)
      - [IPyWidget](panel.pane.ipywidget.md#panel.pane.ipywidget.IPyWidget)
      - [Reacton](panel.pane.ipywidget.md#panel.pane.ipywidget.Reacton)
    - [panel.pane.markup module](panel.pane.markup.md)
      - [DataFrame](panel.pane.markup.md#panel.pane.markup.DataFrame)
      - [HTML](panel.pane.markup.md#panel.pane.markup.HTML)
      - [HTMLBasePane](panel.pane.markup.md#panel.pane.markup.HTMLBasePane)
      - [JSON](panel.pane.markup.md#panel.pane.markup.JSON)
      - [Markdown](panel.pane.markup.md#panel.pane.markup.Markdown)
      - [Str](panel.pane.markup.md#panel.pane.markup.Str)
    - [panel.pane.media module](panel.pane.media.md)
      - [Audio](panel.pane.media.md#panel.pane.media.Audio)
      - [TensorLike](panel.pane.media.md#panel.pane.media.TensorLike)
      - [TensorLikeMeta](panel.pane.media.md#panel.pane.media.TensorLikeMeta)
      - [Video](panel.pane.media.md#panel.pane.media.Video)
    - [panel.pane.perspective module](panel.pane.perspective.md)
      - [Perspective](panel.pane.perspective.md#panel.pane.perspective.Perspective)
      - [Plugin](panel.pane.perspective.md#panel.pane.perspective.Plugin)
      - [deconstruct_pandas()](panel.pane.perspective.md#panel.pane.perspective.deconstruct_pandas)
    - [panel.pane.placeholder module](panel.pane.placeholder.md)
      - [Placeholder](panel.pane.placeholder.md#panel.pane.placeholder.Placeholder)
    - [panel.pane.plot module](panel.pane.plot.md)
      - [Bokeh](panel.pane.plot.md#panel.pane.plot.Bokeh)
      - [Folium](panel.pane.plot.md#panel.pane.plot.Folium)
      - [Matplotlib](panel.pane.plot.md#panel.pane.plot.Matplotlib)
      - [RGGPlot](panel.pane.plot.md#panel.pane.plot.RGGPlot)
      - [YT](panel.pane.plot.md#panel.pane.plot.YT)
    - [panel.pane.plotly module](panel.pane.plotly.md)
      - [Plotly](panel.pane.plotly.md#panel.pane.plotly.Plotly)
    - [panel.pane.streamz module](panel.pane.streamz.md)
      - [Streamz](panel.pane.streamz.md#panel.pane.streamz.Streamz)
    - [panel.pane.textual module](panel.pane.textual.md)
      - [Textual](panel.pane.textual.md#panel.pane.textual.Textual)
    - [panel.pane.vega module](panel.pane.vega.md)
      - [Vega](panel.pane.vega.md#panel.pane.vega.Vega)
      - [ds_as_cds()](panel.pane.vega.md#panel.pane.vega.ds_as_cds)
    - [panel.pane.vizzu module](panel.pane.vizzu.md)
      - [Vizzu](panel.pane.vizzu.md#panel.pane.vizzu.Vizzu)
  - [Module contents](panel.pane.md#module-panel.pane)
    - [Panel panes renders the Python objects you
      know and love ❤️](panel.pane.md#panel-panes-renders-the-python-objects-you-know-and-love)
      - [How to use Panel panes in 2 simple steps](panel.pane.md#how-to-use-panel-panes-in-2-simple-steps)
    - [AVIF](panel.pane.md#panel.pane.AVIF)
    - [Alert](panel.pane.md#panel.pane.Alert)
      - [Alert.applies()](panel.pane.md#panel.pane.Alert.applies)
    - [Audio](panel.pane.md#panel.pane.Audio)
      - [Audio.applies()](panel.pane.md#panel.pane.Audio.applies)
    - [Bokeh](panel.pane.md#panel.pane.Bokeh)
      - [Bokeh.applies()](panel.pane.md#panel.pane.Bokeh.applies)
    - [DataFrame](panel.pane.md#panel.pane.DataFrame)
      - [DataFrame.applies()](panel.pane.md#panel.pane.DataFrame.applies)
    - [DeckGL](panel.pane.md#panel.pane.DeckGL)
      - [DeckGL.applies()](panel.pane.md#panel.pane.DeckGL.applies)
      - [DeckGL.priority](panel.pane.md#panel.pane.DeckGL.priority)
    - [ECharts](panel.pane.md#panel.pane.ECharts)
      - [ECharts.applies()](panel.pane.md#panel.pane.ECharts.applies)
      - [ECharts.js_on_event()](panel.pane.md#panel.pane.ECharts.js_on_event)
      - [ECharts.on_event()](panel.pane.md#panel.pane.ECharts.on_event)
      - [ECharts.priority](panel.pane.md#panel.pane.ECharts.priority)
    - [GIF](panel.pane.md#panel.pane.GIF)
    - [HTML](panel.pane.md#panel.pane.HTML)
      - [HTML.applies()](panel.pane.md#panel.pane.HTML.applies)
      - [HTML.priority](panel.pane.md#panel.pane.HTML.priority)
    - [HoloViews](panel.pane.md#panel.pane.HoloViews)
      - [HoloViews.applies()](panel.pane.md#panel.pane.HoloViews.applies)
      - [HoloViews.jslink()](panel.pane.md#panel.pane.HoloViews.jslink)
      - [HoloViews.widget_layout](panel.pane.md#panel.pane.HoloViews.widget_layout)
    - [ICO](panel.pane.md#panel.pane.ICO)
    - [IPyLeaflet](panel.pane.md#panel.pane.IPyLeaflet)
      - [IPyLeaflet.applies()](panel.pane.md#panel.pane.IPyLeaflet.applies)
    - [IPyWidget](panel.pane.md#panel.pane.IPyWidget)
      - [IPyWidget.applies()](panel.pane.md#panel.pane.IPyWidget.applies)
    - [Interactive](panel.pane.md#panel.pane.Interactive)
      - [Interactive.applies()](panel.pane.md#panel.pane.Interactive.applies)
      - [Interactive.priority](panel.pane.md#panel.pane.Interactive.priority)
    - [JPG](panel.pane.md#panel.pane.JPG)
    - [JSON](panel.pane.md#panel.pane.JSON)
      - [JSON.applies()](panel.pane.md#panel.pane.JSON.applies)
      - [JSON.priority](panel.pane.md#panel.pane.JSON.priority)
    - [LaTeX](panel.pane.md#panel.pane.LaTeX)
      - [LaTeX.applies()](panel.pane.md#panel.pane.LaTeX.applies)
      - [LaTeX.priority](panel.pane.md#panel.pane.LaTeX.priority)
    - [Markdown](panel.pane.md#panel.pane.Markdown)
      - [Markdown.applies()](panel.pane.md#panel.pane.Markdown.applies)
      - [Markdown.priority](panel.pane.md#panel.pane.Markdown.priority)
    - [Matplotlib](panel.pane.md#panel.pane.Matplotlib)
      - [Matplotlib.applies()](panel.pane.md#panel.pane.Matplotlib.applies)
    - [PDF](panel.pane.md#panel.pane.PDF)
    - [PNG](panel.pane.md#panel.pane.PNG)
    - [Pane](panel.pane.md#panel.pane.Pane)
      - [Pane.clone()](panel.pane.md#panel.pane.Pane.clone)
      - [Pane.get_root()](panel.pane.md#panel.pane.Pane.get_root)
    - [PaneBase](panel.pane.md#panel.pane.PaneBase)
      - [PaneBase.applies()](panel.pane.md#panel.pane.PaneBase.applies)
      - [PaneBase.default_layout](panel.pane.md#panel.pane.PaneBase.default_layout)
      - [PaneBase.get_pane_type()](panel.pane.md#panel.pane.PaneBase.get_pane_type)
    - [ParamFunction](panel.pane.md#panel.pane.ParamFunction)
      - [ParamFunction.applies()](panel.pane.md#panel.pane.ParamFunction.applies)
    - [ParamMethod](panel.pane.md#panel.pane.ParamMethod)
      - [ParamMethod.applies()](panel.pane.md#panel.pane.ParamMethod.applies)
    - [ParamRef](panel.pane.md#panel.pane.ParamRef)
      - [ParamRef.applies()](panel.pane.md#panel.pane.ParamRef.applies)
    - [Perspective](panel.pane.md#panel.pane.Perspective)
      - [Perspective.applies()](panel.pane.md#panel.pane.Perspective.applies)
      - [Perspective.on_click()](panel.pane.md#panel.pane.Perspective.on_click)
      - [Perspective.priority](panel.pane.md#panel.pane.Perspective.priority)
    - [Placeholder](panel.pane.md#panel.pane.Placeholder)
      - [Placeholder.update()](panel.pane.md#panel.pane.Placeholder.update)
    - [Plotly](panel.pane.md#panel.pane.Plotly)
      - [Plotly.applies()](panel.pane.md#panel.pane.Plotly.applies)
    - [RGGPlot](panel.pane.md#panel.pane.RGGPlot)
      - [RGGPlot.applies()](panel.pane.md#panel.pane.RGGPlot.applies)
    - [ReactiveExpr](panel.pane.md#panel.pane.ReactiveExpr)
      - [ReactiveExpr.applies()](panel.pane.md#panel.pane.ReactiveExpr.applies)
      - [ReactiveExpr.widget_layout](panel.pane.md#panel.pane.ReactiveExpr.widget_layout)
    - [Reacton](panel.pane.md#panel.pane.Reacton)
      - [Reacton.applies()](panel.pane.md#panel.pane.Reacton.applies)
    - [SVG](panel.pane.md#panel.pane.SVG)
      - [SVG.applies()](panel.pane.md#panel.pane.SVG.applies)
    - [Str](panel.pane.md#panel.pane.Str)
      - [Str.applies()](panel.pane.md#panel.pane.Str.applies)
    - [Streamz](panel.pane.md#panel.pane.Streamz)
      - [Streamz.applies()](panel.pane.md#panel.pane.Streamz.applies)
    - [Textual](panel.pane.md#panel.pane.Textual)
      - [Textual.applies()](panel.pane.md#panel.pane.Textual.applies)
    - [VTK](panel.pane.md#panel.pane.VTK)
    - [VTKVolume](panel.pane.md#panel.pane.VTKVolume)
      - [VTKVolume.applies()](panel.pane.md#panel.pane.VTKVolume.applies)
      - [VTKVolume.register_serializer()](panel.pane.md#panel.pane.VTKVolume.register_serializer)
    - [Vega](panel.pane.md#panel.pane.Vega)
      - [Vega.applies()](panel.pane.md#panel.pane.Vega.applies)
      - [Vega.export()](panel.pane.md#panel.pane.Vega.export)
    - [Video](panel.pane.md#panel.pane.Video)
    - [Vizzu](panel.pane.md#panel.pane.Vizzu)
      - [Vizzu.animate()](panel.pane.md#panel.pane.Vizzu.animate)
      - [Vizzu.applies()](panel.pane.md#panel.pane.Vizzu.applies)
      - [Vizzu.on_click()](panel.pane.md#panel.pane.Vizzu.on_click)
    - [YT](panel.pane.md#panel.pane.YT)
      - [YT.applies()](panel.pane.md#panel.pane.YT.applies)
    - [panel()](panel.pane.md#panel.pane.panel)
- [panel.template
  package](panel.template.md)
  - [Subpackages](panel.template.md#subpackages)
    - [panel.template.bootstrap package](panel.template.bootstrap.md)
      - [Module contents](panel.template.bootstrap.md#module-panel.template.bootstrap)
    - [panel.template.editable package](panel.template.editable.md)
      - [Module contents](panel.template.editable.md#module-panel.template.editable)
    - [panel.template.fast package](panel.template.fast.md)
      - [Subpackages](panel.template.fast.md#subpackages)
      - [Submodules](panel.template.fast.md#submodules)
      - [Module contents](panel.template.fast.md#module-panel.template.fast)
    - [panel.template.golden package](panel.template.golden.md)
      - [Module contents](panel.template.golden.md#module-panel.template.golden)
    - [panel.template.material package](panel.template.material.md)
      - [Module contents](panel.template.material.md#module-panel.template.material)
    - [panel.template.react package](panel.template.react.md)
      - [Module contents](panel.template.react.md#module-panel.template.react)
    - [panel.template.slides package](panel.template.slides.md)
      - [Module contents](panel.template.slides.md#module-panel.template.slides)
    - [panel.template.vanilla package](panel.template.vanilla.md)
      - [Module contents](panel.template.vanilla.md#module-panel.template.vanilla)
  - [Submodules](panel.template.md#submodules)
    - [panel.template.base module](panel.template.base.md)
      - [BaseTemplate](panel.template.base.md#panel.template.base.BaseTemplate)
      - [BasicTemplate](panel.template.base.md#panel.template.base.BasicTemplate)
      - [Template](panel.template.base.md#panel.template.base.Template)
      - [TemplateActions](panel.template.base.md#panel.template.base.TemplateActions)
  - [Module contents](panel.template.md#module-panel.template)
    - [BaseTemplate](panel.template.md#panel.template.BaseTemplate)
      - [BaseTemplate.design](panel.template.md#panel.template.BaseTemplate.design)
      - [BaseTemplate.resolve_resources()](panel.template.md#panel.template.BaseTemplate.resolve_resources)
      - [BaseTemplate.save()](panel.template.md#panel.template.BaseTemplate.save)
      - [BaseTemplate.select()](panel.template.md#panel.template.BaseTemplate.select)
      - [BaseTemplate.servable()](panel.template.md#panel.template.BaseTemplate.servable)
      - [BaseTemplate.server_doc()](panel.template.md#panel.template.BaseTemplate.server_doc)
      - [BaseTemplate.theme](panel.template.md#panel.template.BaseTemplate.theme)
    - [BootstrapTemplate](panel.template.md#panel.template.BootstrapTemplate)
      - [BootstrapTemplate.design](panel.template.md#panel.template.BootstrapTemplate.design)
    - [DarkTheme](panel.template.md#panel.template.DarkTheme)
    - [DefaultTheme](panel.template.md#panel.template.DefaultTheme)
    - [EditableTemplate](panel.template.md#panel.template.EditableTemplate)
    - [FastGridTemplate](panel.template.md#panel.template.FastGridTemplate)
    - [FastListTemplate](panel.template.md#panel.template.FastListTemplate)
    - [GoldenTemplate](panel.template.md#panel.template.GoldenTemplate)
      - [GoldenTemplate.resolve_resources()](panel.template.md#panel.template.GoldenTemplate.resolve_resources)
    - [MaterialTemplate](panel.template.md#panel.template.MaterialTemplate)
      - [MaterialTemplate.design](panel.template.md#panel.template.MaterialTemplate.design)
    - [ReactTemplate](panel.template.md#panel.template.ReactTemplate)
    - [SlidesTemplate](panel.template.md#panel.template.SlidesTemplate)
    - [Template](panel.template.md#panel.template.Template)
      - [Template.add_panel()](panel.template.md#panel.template.Template.add_panel)
      - [Template.add_variable()](panel.template.md#panel.template.Template.add_variable)
    - [VanillaTemplate](panel.template.md#panel.template.VanillaTemplate)
      - [VanillaTemplate.design](panel.template.md#panel.template.VanillaTemplate.design)
- [panel.theme
  package](panel.theme.md)
  - [Submodules](panel.theme.md#submodules)
    - [panel.theme.base module](panel.theme.base.md)
      - [DarkTheme](panel.theme.base.md#panel.theme.base.DarkTheme)
      - [DefaultTheme](panel.theme.base.md#panel.theme.base.DefaultTheme)
      - [Design](panel.theme.base.md#panel.theme.base.Design)
      - [Inherit](panel.theme.base.md#panel.theme.base.Inherit)
      - [Theme](panel.theme.base.md#panel.theme.base.Theme)
    - [panel.theme.bootstrap module](panel.theme.bootstrap.md)
      - [Bootstrap](panel.theme.bootstrap.md#panel.theme.bootstrap.Bootstrap)
      - [BootstrapDarkTheme](panel.theme.bootstrap.md#panel.theme.bootstrap.BootstrapDarkTheme)
      - [BootstrapDefaultTheme](panel.theme.bootstrap.md#panel.theme.bootstrap.BootstrapDefaultTheme)
    - [panel.theme.fast module](panel.theme.fast.md)
      - [Fast](panel.theme.fast.md#panel.theme.fast.Fast)
      - [FastDarkTheme](panel.theme.fast.md#panel.theme.fast.FastDarkTheme)
      - [FastDefaultTheme](panel.theme.fast.md#panel.theme.fast.FastDefaultTheme)
      - [FastStyle](panel.theme.fast.md#panel.theme.fast.FastStyle)
      - [FastThemeMixin](panel.theme.fast.md#panel.theme.fast.FastThemeMixin)
      - [FastWrapper](panel.theme.fast.md#panel.theme.fast.FastWrapper)
    - [panel.theme.material module](panel.theme.material.md)
      - [Material](panel.theme.material.md#panel.theme.material.Material)
      - [MaterialDarkTheme](panel.theme.material.md#panel.theme.material.MaterialDarkTheme)
      - [MaterialDefaultTheme](panel.theme.material.md#panel.theme.material.MaterialDefaultTheme)
      - [MaterialThemeMixin](panel.theme.material.md#panel.theme.material.MaterialThemeMixin)
    - [panel.theme.native module](panel.theme.native.md)
      - [Native](panel.theme.native.md#panel.theme.native.Native)
      - [NativeDarkTheme](panel.theme.native.md#panel.theme.native.NativeDarkTheme)
  - [Module contents](panel.theme.md#module-panel.theme)
    - [Bootstrap](panel.theme.md#panel.theme.Bootstrap)
    - [DarkTheme](panel.theme.md#panel.theme.DarkTheme)
    - [DefaultTheme](panel.theme.md#panel.theme.DefaultTheme)
    - [Design](panel.theme.md#panel.theme.Design)
      - [Design.apply()](panel.theme.md#panel.theme.Design.apply)
      - [Design.apply_bokeh_theme_to_model()](panel.theme.md#panel.theme.Design.apply_bokeh_theme_to_model)
      - [Design.params()](panel.theme.md#panel.theme.Design.params)
      - [Design.resolve_resources()](panel.theme.md#panel.theme.Design.resolve_resources)
    - [Fast](panel.theme.md#panel.theme.Fast)
    - [Inherit](panel.theme.md#panel.theme.Inherit)
    - [Material](panel.theme.md#panel.theme.Material)
    - [Native](panel.theme.md#panel.theme.Native)
    - [Theme](panel.theme.md#panel.theme.Theme)
- [panel.util
  package](panel.util.md)
  - [Submodules](panel.util.md#submodules)
    - [panel.util.checks module](panel.util.checks.md)
      - [isIn()](panel.util.checks.md#panel.util.checks.isIn)
      - [is_holoviews()](panel.util.checks.md#panel.util.checks.is_holoviews)
      - [is_parameterized()](panel.util.checks.md#panel.util.checks.is_parameterized)
      - [isdatetime()](panel.util.checks.md#panel.util.checks.isdatetime)
      - [isfile()](panel.util.checks.md#panel.util.checks.isfile)
    - [panel.util.parameters module](panel.util.parameters.md)
      - [edit_readonly()](panel.util.parameters.md#panel.util.parameters.edit_readonly)
      - [extract_dependencies()](panel.util.parameters.md#panel.util.parameters.extract_dependencies)
      - [get_method_owner()](panel.util.parameters.md#panel.util.parameters.get_method_owner)
      - [recursive_parameterized()](panel.util.parameters.md#panel.util.parameters.recursive_parameterized)
    - [panel.util.warnings module](panel.util.warnings.md)
      - [PanelDeprecationWarning](panel.util.warnings.md#panel.util.warnings.PanelDeprecationWarning)
      - [PanelUserWarning](panel.util.warnings.md#panel.util.warnings.PanelUserWarning)
      - [find_stack_level()](panel.util.warnings.md#panel.util.warnings.find_stack_level)
  - [Module contents](panel.util.md#module-panel.util)
    - [LazyHTMLSanitizer](panel.util.md#panel.util.LazyHTMLSanitizer)
    - [abbreviated_repr()](panel.util.md#panel.util.abbreviated_repr)
    - [base_version()](panel.util.md#panel.util.base_version)
    - [datetime_as_utctimestamp()](panel.util.md#panel.util.datetime_as_utctimestamp)
    - [decode_token()](panel.util.md#panel.util.decode_token)
    - [flatten()](panel.util.md#panel.util.flatten)
    - [full_groupby()](panel.util.md#panel.util.full_groupby)
    - [fullpath()](panel.util.md#panel.util.fullpath)
    - [function_name()](panel.util.md#panel.util.function_name)
    - [indexOf()](panel.util.md#panel.util.indexOf)
    - [param_name()](panel.util.md#panel.util.param_name)
    - [param_reprs()](panel.util.md#panel.util.param_reprs)
    - [parse_query()](panel.util.md#panel.util.parse_query)
    - [prefix_length()](panel.util.md#panel.util.prefix_length)
    - [set_bokeh_validation()](panel.util.md#panel.util.set_bokeh_validation)
    - [styler_update()](panel.util.md#panel.util.styler_update)
    - [unique_iterator()](panel.util.md#panel.util.unique_iterator)
    - [url_path()](panel.util.md#panel.util.url_path)
    - [value_as_datetime()](panel.util.md#panel.util.value_as_datetime)
- [panel.widgets
  package](panel.widgets.md)
  - [Submodules](panel.widgets.md#submodules)
    - [panel.widgets.base module](panel.widgets.base.md)
      - [CompositeWidget](panel.widgets.base.md#panel.widgets.base.CompositeWidget)
      - [Widget](panel.widgets.base.md#panel.widgets.base.Widget)
      - [WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase)
    - [panel.widgets.button module](panel.widgets.button.md)
      - [Button](panel.widgets.button.md#panel.widgets.button.Button)
      - [IconMixin](panel.widgets.button.md#panel.widgets.button.IconMixin)
      - [MenuButton](panel.widgets.button.md#panel.widgets.button.MenuButton)
      - [Toggle](panel.widgets.button.md#panel.widgets.button.Toggle)
    - [panel.widgets.codeeditor module](panel.widgets.codeeditor.md)
      - [CodeEditor](panel.widgets.codeeditor.md#panel.widgets.codeeditor.CodeEditor)
    - [panel.widgets.debugger module](panel.widgets.debugger.md)
      - [CheckFilter](panel.widgets.debugger.md#panel.widgets.debugger.CheckFilter)
      - [Debugger](panel.widgets.debugger.md#panel.widgets.debugger.Debugger)
      - [DebuggerButtons](panel.widgets.debugger.md#panel.widgets.debugger.DebuggerButtons)
      - [TermFormatter](panel.widgets.debugger.md#panel.widgets.debugger.TermFormatter)
    - [panel.widgets.file_selector module](panel.widgets.file_selector.md)
      - [BaseFileNavigator](panel.widgets.file_selector.md#panel.widgets.file_selector.BaseFileNavigator)
      - [BaseFileSelector](panel.widgets.file_selector.md#panel.widgets.file_selector.BaseFileSelector)
      - [FileSelector](panel.widgets.file_selector.md#panel.widgets.file_selector.FileSelector)
    - [panel.widgets.icon module](panel.widgets.icon.md)
      - [ButtonIcon](panel.widgets.icon.md#panel.widgets.icon.ButtonIcon)
      - [ToggleIcon](panel.widgets.icon.md#panel.widgets.icon.ToggleIcon)
    - [panel.widgets.indicators module](panel.widgets.indicators.md)
      - [Indicators](panel.widgets.indicators.md#indicators)
      - [BooleanIndicator](panel.widgets.indicators.md#panel.widgets.indicators.BooleanIndicator)
      - [BooleanStatus](panel.widgets.indicators.md#panel.widgets.indicators.BooleanStatus)
      - [Dial](panel.widgets.indicators.md#panel.widgets.indicators.Dial)
      - [Gauge](panel.widgets.indicators.md#panel.widgets.indicators.Gauge)
      - [LinearGauge](panel.widgets.indicators.md#panel.widgets.indicators.LinearGauge)
      - [LoadingSpinner](panel.widgets.indicators.md#panel.widgets.indicators.LoadingSpinner)
      - [Number](panel.widgets.indicators.md#panel.widgets.indicators.Number)
      - [Progress](panel.widgets.indicators.md#panel.widgets.indicators.Progress)
      - [String](panel.widgets.indicators.md#panel.widgets.indicators.String)
      - [TooltipIcon](panel.widgets.indicators.md#panel.widgets.indicators.TooltipIcon)
      - [Tqdm](panel.widgets.indicators.md#panel.widgets.indicators.Tqdm)
      - [Trend](panel.widgets.indicators.md#panel.widgets.indicators.Trend)
      - [ValueIndicator](panel.widgets.indicators.md#panel.widgets.indicators.ValueIndicator)
    - [panel.widgets.input module](panel.widgets.input.md)
      - [ArrayInput](panel.widgets.input.md#panel.widgets.input.ArrayInput)
      - [Checkbox](panel.widgets.input.md#panel.widgets.input.Checkbox)
      - [ColorPicker](panel.widgets.input.md#panel.widgets.input.ColorPicker)
      - [DatePicker](panel.widgets.input.md#panel.widgets.input.DatePicker)
      - [DateRangePicker](panel.widgets.input.md#panel.widgets.input.DateRangePicker)
      - [DatetimeInput](panel.widgets.input.md#panel.widgets.input.DatetimeInput)
      - [DatetimePicker](panel.widgets.input.md#panel.widgets.input.DatetimePicker)
      - [DatetimeRangeInput](panel.widgets.input.md#panel.widgets.input.DatetimeRangeInput)
      - [DatetimeRangePicker](panel.widgets.input.md#panel.widgets.input.DatetimeRangePicker)
      - [FileDropper](panel.widgets.input.md#panel.widgets.input.FileDropper)
      - [FileInput](panel.widgets.input.md#panel.widgets.input.FileInput)
      - [FloatInput](panel.widgets.input.md#panel.widgets.input.FloatInput)
      - [IntInput](panel.widgets.input.md#panel.widgets.input.IntInput)
      - [LiteralInput](panel.widgets.input.md#panel.widgets.input.LiteralInput)
      - [NumberInput](panel.widgets.input.md#panel.widgets.input.NumberInput)
      - [PasswordInput](panel.widgets.input.md#panel.widgets.input.PasswordInput)
      - [Spinner](panel.widgets.input.md#panel.widgets.input.Spinner)
      - [StaticText](panel.widgets.input.md#panel.widgets.input.StaticText)
      - [Switch](panel.widgets.input.md#panel.widgets.input.Switch)
      - [TextAreaInput](panel.widgets.input.md#panel.widgets.input.TextAreaInput)
      - [TextInput](panel.widgets.input.md#panel.widgets.input.TextInput)
      - [TimePicker](panel.widgets.input.md#panel.widgets.input.TimePicker)
    - [panel.widgets.misc module](panel.widgets.misc.md)
      - [FileDownload](panel.widgets.misc.md#panel.widgets.misc.FileDownload)
      - [JSONEditor](panel.widgets.misc.md#panel.widgets.misc.JSONEditor)
      - [VideoStream](panel.widgets.misc.md#panel.widgets.misc.VideoStream)
    - [panel.widgets.player module](panel.widgets.player.md)
      - [DiscretePlayer](panel.widgets.player.md#panel.widgets.player.DiscretePlayer)
      - [Player](panel.widgets.player.md#panel.widgets.player.Player)
      - [PlayerBase](panel.widgets.player.md#panel.widgets.player.PlayerBase)
    - [panel.widgets.select module](panel.widgets.select.md)
      - [AutocompleteInput](panel.widgets.select.md#panel.widgets.select.AutocompleteInput)
      - [CheckBoxGroup](panel.widgets.select.md#panel.widgets.select.CheckBoxGroup)
      - [CheckButtonGroup](panel.widgets.select.md#panel.widgets.select.CheckButtonGroup)
      - [ColorMap](panel.widgets.select.md#panel.widgets.select.ColorMap)
      - [CrossSelector](panel.widgets.select.md#panel.widgets.select.CrossSelector)
      - [MultiChoice](panel.widgets.select.md#panel.widgets.select.MultiChoice)
      - [MultiSelect](panel.widgets.select.md#panel.widgets.select.MultiSelect)
      - [NestedSelect](panel.widgets.select.md#panel.widgets.select.NestedSelect)
      - [RadioBoxGroup](panel.widgets.select.md#panel.widgets.select.RadioBoxGroup)
      - [RadioButtonGroup](panel.widgets.select.md#panel.widgets.select.RadioButtonGroup)
      - [Select](panel.widgets.select.md#panel.widgets.select.Select)
      - [SelectBase](panel.widgets.select.md#panel.widgets.select.SelectBase)
      - [SingleSelectBase](panel.widgets.select.md#panel.widgets.select.SingleSelectBase)
      - [ToggleGroup](panel.widgets.select.md#panel.widgets.select.ToggleGroup)
    - [panel.widgets.slider module](panel.widgets.slider.md)
      - [ContinuousSlider](panel.widgets.slider.md#panel.widgets.slider.ContinuousSlider)
      - [DateRangeSlider](panel.widgets.slider.md#panel.widgets.slider.DateRangeSlider)
      - [DateSlider](panel.widgets.slider.md#panel.widgets.slider.DateSlider)
      - [DatetimeRangeSlider](panel.widgets.slider.md#panel.widgets.slider.DatetimeRangeSlider)
      - [DatetimeSlider](panel.widgets.slider.md#panel.widgets.slider.DatetimeSlider)
      - [DiscreteSlider](panel.widgets.slider.md#panel.widgets.slider.DiscreteSlider)
      - [EditableFloatSlider](panel.widgets.slider.md#panel.widgets.slider.EditableFloatSlider)
      - [EditableIntSlider](panel.widgets.slider.md#panel.widgets.slider.EditableIntSlider)
      - [EditableRangeSlider](panel.widgets.slider.md#panel.widgets.slider.EditableRangeSlider)
      - [FloatSlider](panel.widgets.slider.md#panel.widgets.slider.FloatSlider)
      - [IntRangeSlider](panel.widgets.slider.md#panel.widgets.slider.IntRangeSlider)
      - [IntSlider](panel.widgets.slider.md#panel.widgets.slider.IntSlider)
      - [RangeSlider](panel.widgets.slider.md#panel.widgets.slider.RangeSlider)
    - [panel.widgets.speech_to_text module](panel.widgets.speech_to_text.md)
      - [Grammar](panel.widgets.speech_to_text.md#panel.widgets.speech_to_text.Grammar)
      - [GrammarList](panel.widgets.speech_to_text.md#panel.widgets.speech_to_text.GrammarList)
      - [Language](panel.widgets.speech_to_text.md#panel.widgets.speech_to_text.Language)
      - [RecognitionAlternative](panel.widgets.speech_to_text.md#panel.widgets.speech_to_text.RecognitionAlternative)
      - [RecognitionResult](panel.widgets.speech_to_text.md#panel.widgets.speech_to_text.RecognitionResult)
      - [SpeechToText](panel.widgets.speech_to_text.md#panel.widgets.speech_to_text.SpeechToText)
    - [panel.widgets.tables module](panel.widgets.tables.md)
      - [BaseTable](panel.widgets.tables.md#panel.widgets.tables.BaseTable)
      - [ColumnSpec](panel.widgets.tables.md#panel.widgets.tables.ColumnSpec)
      - [DataFrame](panel.widgets.tables.md#panel.widgets.tables.DataFrame)
      - [GroupSpec](panel.widgets.tables.md#panel.widgets.tables.GroupSpec)
      - [Tabulator](panel.widgets.tables.md#panel.widgets.tables.Tabulator)
    - [panel.widgets.terminal module](panel.widgets.terminal.md)
      - [Terminal](panel.widgets.terminal.md#panel.widgets.terminal.Terminal)
      - [TerminalSubprocess](panel.widgets.terminal.md#panel.widgets.terminal.TerminalSubprocess)
    - [panel.widgets.text_to_speech module](panel.widgets.text_to_speech.md)
      - [TextToSpeech](panel.widgets.text_to_speech.md#panel.widgets.text_to_speech.TextToSpeech)
      - [Utterance](panel.widgets.text_to_speech.md#panel.widgets.text_to_speech.Utterance)
      - [Voice](panel.widgets.text_to_speech.md#panel.widgets.text_to_speech.Voice)
    - [panel.widgets.texteditor module](panel.widgets.texteditor.md)
      - [TextEditor](panel.widgets.texteditor.md#panel.widgets.texteditor.TextEditor)
    - [panel.widgets.widget module](panel.widgets.widget.md)
      - [fixed](panel.widgets.widget.md#panel.widgets.widget.fixed)
      - [widget](panel.widgets.widget.md#panel.widgets.widget.widget)
  - [Module contents](panel.widgets.md#module-panel.widgets)
    - [Panel widgets makes your data exploration and
      apps interactive](panel.widgets.md#panel-widgets-makes-your-data-exploration-and-apps-interactive)
      - [How to use Panel widgets in 4 simple
        steps](panel.widgets.md#how-to-use-panel-widgets-in-4-simple-steps)
    - [ArrayInput](panel.widgets.md#panel.widgets.ArrayInput)
    - [AutocompleteInput](panel.widgets.md#panel.widgets.AutocompleteInput)
    - [BooleanStatus](panel.widgets.md#panel.widgets.BooleanStatus)
    - [Button](panel.widgets.md#panel.widgets.Button)
      - [Button.jslink()](panel.widgets.md#panel.widgets.Button.jslink)
      - [Button.on_click()](panel.widgets.md#panel.widgets.Button.on_click)
    - [ButtonIcon](panel.widgets.md#panel.widgets.ButtonIcon)
      - [ButtonIcon.on_click()](panel.widgets.md#panel.widgets.ButtonIcon.on_click)
    - [CheckBoxGroup](panel.widgets.md#panel.widgets.CheckBoxGroup)
    - [CheckButtonGroup](panel.widgets.md#panel.widgets.CheckButtonGroup)
    - [Checkbox](panel.widgets.md#panel.widgets.Checkbox)
    - [CodeEditor](panel.widgets.md#panel.widgets.CodeEditor)
    - [ColorPicker](panel.widgets.md#panel.widgets.ColorPicker)
    - [CompositeWidget](panel.widgets.md#panel.widgets.CompositeWidget)
      - [CompositeWidget.select()](panel.widgets.md#panel.widgets.CompositeWidget.select)
    - [CrossSelector](panel.widgets.md#panel.widgets.CrossSelector)
      - [CrossSelector.filter_fn()](panel.widgets.md#panel.widgets.CrossSelector.filter_fn)
    - [DataFrame](panel.widgets.md#panel.widgets.DataFrame)
    - [DatePicker](panel.widgets.md#panel.widgets.DatePicker)
    - [DateRangePicker](panel.widgets.md#panel.widgets.DateRangePicker)
    - [DateRangeSlider](panel.widgets.md#panel.widgets.DateRangeSlider)
    - [DateSlider](panel.widgets.md#panel.widgets.DateSlider)
    - [DatetimeInput](panel.widgets.md#panel.widgets.DatetimeInput)
      - [DatetimeInput.type](panel.widgets.md#panel.widgets.DatetimeInput.type)
    - [DatetimePicker](panel.widgets.md#panel.widgets.DatetimePicker)
    - [DatetimeRangeInput](panel.widgets.md#panel.widgets.DatetimeRangeInput)
    - [DatetimeRangePicker](panel.widgets.md#panel.widgets.DatetimeRangePicker)
    - [DatetimeRangeSlider](panel.widgets.md#panel.widgets.DatetimeRangeSlider)
    - [DatetimeSlider](panel.widgets.md#panel.widgets.DatetimeSlider)
    - [Debugger](panel.widgets.md#panel.widgets.Debugger)
    - [Dial](panel.widgets.md#panel.widgets.Dial)
    - [DiscretePlayer](panel.widgets.md#panel.widgets.DiscretePlayer)
    - [DiscreteSlider](panel.widgets.md#panel.widgets.DiscreteSlider)
      - [DiscreteSlider.labels](panel.widgets.md#panel.widgets.DiscreteSlider.labels)
      - [DiscreteSlider.values](panel.widgets.md#panel.widgets.DiscreteSlider.values)
    - [EditableFloatSlider](panel.widgets.md#panel.widgets.EditableFloatSlider)
    - [EditableIntSlider](panel.widgets.md#panel.widgets.EditableIntSlider)
    - [EditableRangeSlider](panel.widgets.md#panel.widgets.EditableRangeSlider)
    - [FileDownload](panel.widgets.md#panel.widgets.FileDownload)
    - [FileDropper](panel.widgets.md#panel.widgets.FileDropper)
    - [FileInput](panel.widgets.md#panel.widgets.FileInput)
      - [FileInput.clear()](panel.widgets.md#panel.widgets.FileInput.clear)
      - [FileInput.save()](panel.widgets.md#panel.widgets.FileInput.save)
    - [FileSelector](panel.widgets.md#panel.widgets.FileSelector)
    - [FloatInput](panel.widgets.md#panel.widgets.FloatInput)
    - [FloatSlider](panel.widgets.md#panel.widgets.FloatSlider)
    - [Gauge](panel.widgets.md#panel.widgets.Gauge)
    - [Grammar](panel.widgets.md#panel.widgets.Grammar)
      - [Grammar.serialize()](panel.widgets.md#panel.widgets.Grammar.serialize)
    - [GrammarList](panel.widgets.md#panel.widgets.GrammarList)
      - [GrammarList.add_from_string()](panel.widgets.md#panel.widgets.GrammarList.add_from_string)
      - [GrammarList.add_from_uri()](panel.widgets.md#panel.widgets.GrammarList.add_from_uri)
      - [GrammarList.serialize()](panel.widgets.md#panel.widgets.GrammarList.serialize)
    - [IntInput](panel.widgets.md#panel.widgets.IntInput)
    - [IntRangeSlider](panel.widgets.md#panel.widgets.IntRangeSlider)
    - [IntSlider](panel.widgets.md#panel.widgets.IntSlider)
    - [JSONEditor](panel.widgets.md#panel.widgets.JSONEditor)
    - [LinearGauge](panel.widgets.md#panel.widgets.LinearGauge)
    - [LiteralInput](panel.widgets.md#panel.widgets.LiteralInput)
    - [LoadingSpinner](panel.widgets.md#panel.widgets.LoadingSpinner)
    - [MenuButton](panel.widgets.md#panel.widgets.MenuButton)
      - [MenuButton.on_click()](panel.widgets.md#panel.widgets.MenuButton.on_click)
    - [MultiChoice](panel.widgets.md#panel.widgets.MultiChoice)
    - [MultiSelect](panel.widgets.md#panel.widgets.MultiSelect)
      - [MultiSelect.on_double_click()](panel.widgets.md#panel.widgets.MultiSelect.on_double_click)
    - [NestedSelect](panel.widgets.md#panel.widgets.NestedSelect)
      - [NestedSelect.layout](panel.widgets.md#panel.widgets.NestedSelect.layout)
    - [Number](panel.widgets.md#panel.widgets.Number)
    - [NumberInput](panel.widgets.md#panel.widgets.NumberInput)
    - [PasswordInput](panel.widgets.md#panel.widgets.PasswordInput)
    - [Player](panel.widgets.md#panel.widgets.Player)
    - [Progress](panel.widgets.md#panel.widgets.Progress)
      - [Progress.sizing_mode](panel.widgets.md#panel.widgets.Progress.sizing_mode)
    - [RadioBoxGroup](panel.widgets.md#panel.widgets.RadioBoxGroup)
    - [RadioButtonGroup](panel.widgets.md#panel.widgets.RadioButtonGroup)
    - [RangeSlider](panel.widgets.md#panel.widgets.RangeSlider)
    - [Select](panel.widgets.md#panel.widgets.Select)
    - [SpeechToText](panel.widgets.md#panel.widgets.SpeechToText)
      - [SpeechToText.results_as_html](panel.widgets.md#panel.widgets.SpeechToText.results_as_html)
      - [SpeechToText.results_deserialized](panel.widgets.md#panel.widgets.SpeechToText.results_deserialized)
    - [Spinner](panel.widgets.md#panel.widgets.Spinner)
    - [StaticText](panel.widgets.md#panel.widgets.StaticText)
    - [Switch](panel.widgets.md#panel.widgets.Switch)
    - [Tabulator](panel.widgets.md#panel.widgets.Tabulator)
      - [Tabulator.current_view](panel.widgets.md#panel.widgets.Tabulator.current_view)
      - [Tabulator.download()](panel.widgets.md#panel.widgets.Tabulator.download)
      - [Tabulator.download_menu()](panel.widgets.md#panel.widgets.Tabulator.download_menu)
      - [Tabulator.on_click()](panel.widgets.md#panel.widgets.Tabulator.on_click)
      - [Tabulator.on_edit()](panel.widgets.md#panel.widgets.Tabulator.on_edit)
      - [Tabulator.stream()](panel.widgets.md#panel.widgets.Tabulator.stream)
    - [Terminal](panel.widgets.md#panel.widgets.Terminal)
      - [Terminal.subprocess](panel.widgets.md#panel.widgets.Terminal.subprocess)
    - [TextAreaInput](panel.widgets.md#panel.widgets.TextAreaInput)
    - [TextEditor](panel.widgets.md#panel.widgets.TextEditor)
    - [TextInput](panel.widgets.md#panel.widgets.TextInput)
    - [TextToSpeech](panel.widgets.md#panel.widgets.TextToSpeech)
    - [TimePicker](panel.widgets.md#panel.widgets.TimePicker)
    - [Toggle](panel.widgets.md#panel.widgets.Toggle)
    - [ToggleGroup](panel.widgets.md#panel.widgets.ToggleGroup)
    - [ToggleIcon](panel.widgets.md#panel.widgets.ToggleIcon)
    - [TooltipIcon](panel.widgets.md#panel.widgets.TooltipIcon)
    - [Tqdm](panel.widgets.md#panel.widgets.Tqdm)
      - [Tqdm.reset()](panel.widgets.md#panel.widgets.Tqdm.reset)
    - [Trend](panel.widgets.md#panel.widgets.Trend)
      - [Trend.sizing_mode](panel.widgets.md#panel.widgets.Trend.sizing_mode)
    - [Utterance](panel.widgets.md#panel.widgets.Utterance)
      - [Utterance.set_voices()](panel.widgets.md#panel.widgets.Utterance.set_voices)
      - [Utterance.to_dict()](panel.widgets.md#panel.widgets.Utterance.to_dict)
    - [VideoStream](panel.widgets.md#panel.widgets.VideoStream)
      - [VideoStream.snapshot()](panel.widgets.md#panel.widgets.VideoStream.snapshot)
    - [Voice](panel.widgets.md#panel.widgets.Voice)
      - [Voice.group_by_lang()](panel.widgets.md#panel.widgets.Voice.group_by_lang)
      - [Voice.to_voices_list()](panel.widgets.md#panel.widgets.Voice.to_voices_list)
    - [Widget](panel.widgets.md#panel.widgets.Widget)
    - [WidgetBase](panel.widgets.md#panel.widgets.WidgetBase)
      - [WidgetBase.from_param()](panel.widgets.md#panel.widgets.WidgetBase.from_param)
      - [WidgetBase.from_values()](panel.widgets.md#panel.widgets.WidgetBase.from_values)

## Submodules

- [panel.auth
  module](panel.auth.md)
  - [Auth0Handler](panel.auth.md#panel.auth.Auth0Handler)
  - [AzureAdLoginHandler](panel.auth.md#panel.auth.AzureAdLoginHandler)
  - [AzureAdV2LoginHandler](panel.auth.md#panel.auth.AzureAdV2LoginHandler)
  - [BasicAuthProvider](panel.auth.md#panel.auth.BasicAuthProvider)
    - [BasicAuthProvider.get_user](panel.auth.md#panel.auth.BasicAuthProvider.get_user)
    - [BasicAuthProvider.login_handler](panel.auth.md#panel.auth.BasicAuthProvider.login_handler)
    - [BasicAuthProvider.login_url](panel.auth.md#panel.auth.BasicAuthProvider.login_url)
    - [BasicAuthProvider.logout_handler](panel.auth.md#panel.auth.BasicAuthProvider.logout_handler)
    - [BasicAuthProvider.logout_url](panel.auth.md#panel.auth.BasicAuthProvider.logout_url)
  - [BasicLoginHandler](panel.auth.md#panel.auth.BasicLoginHandler)
  - [BitbucketLoginHandler](panel.auth.md#panel.auth.BitbucketLoginHandler)
  - [CodeChallengeLoginHandler](panel.auth.md#panel.auth.CodeChallengeLoginHandler)
  - [GenericLoginHandler](panel.auth.md#panel.auth.GenericLoginHandler)
  - [GitLabLoginHandler](panel.auth.md#panel.auth.GitLabLoginHandler)
  - [GithubLoginHandler](panel.auth.md#panel.auth.GithubLoginHandler)
  - [GoogleLoginHandler](panel.auth.md#panel.auth.GoogleLoginHandler)
  - [LogoutHandler](panel.auth.md#panel.auth.LogoutHandler)
  - [OAuthLoginHandler](panel.auth.md#panel.auth.OAuthLoginHandler)
    - [OAuthLoginHandler.get_authenticated_user()](panel.auth.md#panel.auth.OAuthLoginHandler.get_authenticated_user)
    - [OAuthLoginHandler.get_state_cookie()](panel.auth.md#panel.auth.OAuthLoginHandler.get_state_cookie)
    - [OAuthLoginHandler.write_error()](panel.auth.md#panel.auth.OAuthLoginHandler.write_error)
  - [OAuthProvider](panel.auth.md#panel.auth.OAuthProvider)
    - [OAuthProvider.get_user](panel.auth.md#panel.auth.OAuthProvider.get_user)
    - [OAuthProvider.get_user_async](panel.auth.md#panel.auth.OAuthProvider.get_user_async)
    - [OAuthProvider.login_handler](panel.auth.md#panel.auth.OAuthProvider.login_handler)
  - [OktaLoginHandler](panel.auth.md#panel.auth.OktaLoginHandler)
  - [PAMLoginHandler](panel.auth.md#panel.auth.PAMLoginHandler)
  - [PasswordLoginHandler](panel.auth.md#panel.auth.PasswordLoginHandler)
  - [decode_response_body()](panel.auth.md#panel.auth.decode_response_body)
  - [extract_urlparam()](panel.auth.md#panel.auth.extract_urlparam)
- [panel.compiler
  module](panel.compiler.md)
- [panel.config
  module](panel.config.md)
  - [panel_extension](panel.config.md#panel.config.panel_extension)
- [panel.custom
  module](panel.custom.md)
  - [AnyWidgetComponent](panel.custom.md#panel.custom.AnyWidgetComponent)
    - [AnyWidgetComponent.send()](panel.custom.md#panel.custom.AnyWidgetComponent.send)
  - [JSComponent](panel.custom.md#panel.custom.JSComponent)
  - [PyComponent](panel.custom.md#panel.custom.PyComponent)
    - [PyComponent.select()](panel.custom.md#panel.custom.PyComponent.select)
  - [ReactComponent](panel.custom.md#panel.custom.ReactComponent)
  - [ReactiveESM](panel.custom.md#panel.custom.ReactiveESM)
    - [ReactiveESM.on_event()](panel.custom.md#panel.custom.ReactiveESM.on_event)
    - [ReactiveESM.on_msg()](panel.custom.md#panel.custom.ReactiveESM.on_msg)
    - [ReactiveESM.select()](panel.custom.md#panel.custom.ReactiveESM.select)
  - [ReactiveESMMetaclass](panel.custom.md#panel.custom.ReactiveESMMetaclass)
- [panel.depends
  module](panel.depends.md)
  - [bind()](panel.depends.md#panel.depends.bind)
  - [depends()](panel.depends.md#panel.depends.depends)
- [panel.entry_points module](panel.entry_points.md)
- [panel.interact
  module](panel.interact.md)
  - [interactive](panel.interact.md#panel.interact.interactive)
    - [interactive.applies()](panel.interact.md#panel.interact.interactive.applies)
    - [interactive.default_layout](panel.interact.md#panel.interact.interactive.default_layout)
    - [interactive.find_abbreviations()](panel.interact.md#panel.interact.interactive.find_abbreviations)
    - [interactive.widgets_from_abbreviations()](panel.interact.md#panel.interact.interactive.widgets_from_abbreviations)
- [panel.links
  module](panel.links.md)
  - [Callback](panel.links.md#panel.links.Callback)
    - [Callback.init()](panel.links.md#panel.links.Callback.init)
    - [Callback.register_callback()](panel.links.md#panel.links.Callback.register_callback)
    - [Callback.unwatch()](panel.links.md#panel.links.Callback.unwatch)
  - [Link](panel.links.md#panel.links.Link)
    - [Link.link()](panel.links.md#panel.links.Link.link)
    - [Link.unlink()](panel.links.md#panel.links.Link.unlink)
- [panel.param
  module](panel.param.md)
  - [Param](panel.param.md#panel.param.Param)
    - [Param.applies()](panel.param.md#panel.param.Param.applies)
    - [Param.default_layout](panel.param.md#panel.param.Param.default_layout)
    - [Param.expand_layout](panel.param.md#panel.param.Param.expand_layout)
    - [Param.get_root()](panel.param.md#panel.param.Param.get_root)
    - [Param.select()](panel.param.md#panel.param.Param.select)
    - [Param.widget()](panel.param.md#panel.param.Param.widget)
  - [ParamFunction](panel.param.md#panel.param.ParamFunction)
    - [ParamFunction.applies()](panel.param.md#panel.param.ParamFunction.applies)
  - [ParamMethod](panel.param.md#panel.param.ParamMethod)
    - [ParamMethod.applies()](panel.param.md#panel.param.ParamMethod.applies)
  - [ReactiveExpr](panel.param.md#panel.param.ReactiveExpr)
    - [ReactiveExpr.applies()](panel.param.md#panel.param.ReactiveExpr.applies)
    - [ReactiveExpr.widget_layout](panel.param.md#panel.param.ReactiveExpr.widget_layout)
  - [set_values()](panel.param.md#panel.param.set_values)
- [panel.pipeline
  module](panel.pipeline.md)
  - [Pipeline](panel.pipeline.md#panel.pipeline.Pipeline)
    - [Pipeline.add_stage()](panel.pipeline.md#panel.pipeline.Pipeline.add_stage)
    - [Pipeline.define_graph()](panel.pipeline.md#panel.pipeline.Pipeline.define_graph)
- [panel.reactive
  module](panel.reactive.md)
  - [Reactive](panel.reactive.md#panel.reactive.Reactive)
    - [Reactive.controls()](panel.reactive.md#panel.reactive.Reactive.controls)
    - [Reactive.jscallback()](panel.reactive.md#panel.reactive.Reactive.jscallback)
    - [Reactive.jslink()](panel.reactive.md#panel.reactive.Reactive.jslink)
    - [Reactive.link()](panel.reactive.md#panel.reactive.Reactive.link)
  - [ReactiveData](panel.reactive.md#panel.reactive.ReactiveData)
  - [ReactiveHTML](panel.reactive.md#panel.reactive.ReactiveHTML)
    - [ReactiveHTML.on_event()](panel.reactive.md#panel.reactive.ReactiveHTML.on_event)
- [panel.viewable
  module](panel.viewable.md)
  - [Layoutable](panel.viewable.md#panel.viewable.Layoutable)
  - [Viewable](panel.viewable.md#panel.viewable.Viewable)
    - [Viewable.clone()](panel.viewable.md#panel.viewable.Viewable.clone)
    - [Viewable.embed()](panel.viewable.md#panel.viewable.Viewable.embed)
    - [Viewable.save()](panel.viewable.md#panel.viewable.Viewable.save)
    - [Viewable.select()](panel.viewable.md#panel.viewable.Viewable.select)
    - [Viewable.server_doc()](panel.viewable.md#panel.viewable.Viewable.server_doc)
  - [Viewer](panel.viewable.md#panel.viewable.Viewer)
    - [Viewer.servable()](panel.viewable.md#panel.viewable.Viewer.servable)
    - [Viewer.show()](panel.viewable.md#panel.viewable.Viewer.show)

## Module contents

### Panel is a high level app and dashboarding framework

Panel is an open-source Python library that lets you create custom
interactive web apps and dashboards by connecting user-defined widgets
to plots, images, tables, or text.

Panel works with the tools you know and ❤️.

Check out [https://panel.holoviz.org/](https://panel.holoviz.org/)

<figure id="id1" class="align-default">

<figcaption aria-hidden="true">Panel
Dashboard</figcaption>
</figure>

#### How to develop a Panel app in 3 simple steps

- Write the app

\>\>\>
import
panel
as
pn \>\>\>
pn.extension(sizing_mode="stretch_width",
template="fast")
\>\>\>
pn.state.template.param.update(title="My
Data App") \>\>\>
pn.panel(some_python_object).servable()

- Run your app

\$ panel serve my_script.py –dev –show

or

\$ panel serve my_notebook.ipynb –dev –show

The app will be available in your browser!

- Change your code and save it

The app will reload with your changes!

You can also add automatic reload to jupyterlab. Check out
[https://blog.holoviz.org/panel_0.12.0.html#JupyterLab-previews](https://blog.holoviz.org/panel_0.12.0.html#JupyterLab-previews)

To learn more about Panel check out
[https://panel.holoviz.org/getting_started/index.html](https://panel.holoviz.org/getting_started/index.html)

class panel.Accordion(\*objects, **params)
Bases: [NamedListPanel](panel.layout.base.md#panel.layout.base.NamedListPanel)

The Accordion layout is a type of Card layout that allows switching
between multiple objects by clicking on the corresponding card header.

The labels for each card will default to the name parameter of the
card’s contents, but may also be defined explicitly as part of a tuple.

Like Column and Row, Accordion has a list-like API that allows
interactively updating and modifying the cards using the methods append,
extend, clear, insert, pop, remove and \_\_setitem\_\_.

Reference:
[https://panel.holoviz.org/reference/layouts/Accordion.html](https://panel.holoviz.org/reference/layouts/Accordion.html)

Example:

\>\>\>
pn.Accordion(some_pane_with_a_name,
("Plot",
some_plot))

Methods

|  |  |
|----|----|
| [select](#panel.Accordion.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, margin, styles, stylesheets, tags,
> width, width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.layout.base.NamedListLike"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.NamedListLike](panel.layout.base.md#panel.layout.base.NamedListLike):
> objects
>
> [class="reference internal"
> title="panel.layout.base.NamedListPanel"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.NamedListPanel](panel.layout.base.md#panel.layout.base.NamedListPanel):
> scroll
>
>

`active`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'int'>,`` ``label='Active')`
List of indexes of active cards.

`active_header_background`` ``=`` ``String(allow_None=True,`` ``label='Active`` ``header`` ``background')`
Color for currently active headers.

`header_color`` ``=`` ``String(default='',`` ``label='Header`` ``color')`
A valid CSS color to apply to the expand button.

`header_background`` ``=`` ``String(default='',`` ``label='Header`` ``background')`
A valid CSS color for the header background.

`toggle`` ``=`` ``Boolean(default=False,`` ``label='Toggle')`
Whether to toggle between active cards or allow multiple cards

select(selector: type \| Callable\[\[Viewable\], bool\] \| None = None) → list\[Viewable\]
Iterates over the Viewable and any potential children in the applying
the Selector.

Parameters:
**selector: type or callable or None**
The selector allows selecting a subset of Viewables by declaring a type
or callable function to filter by.

Returns:
viewables: list(Viewable)

class panel.Card(\*objects, **params)
Bases: [Column](panel.layout.base.md#panel.layout.base.Column)

A Card layout allows arranging multiple panel objects in a collapsible,
vertical container with a header bar.

Reference:
[https://panel.holoviz.org/reference/layouts/Card.html](https://panel.holoviz.org/reference/layouts/Card.html)

Example:

\>\>\>
pn.Card(
...
some_widget,
some_pane,
some_python_object,
...
title='Card',
styles=dict(background='WhiteSmoke'),
... )

Methods

|  |  |
|----|----|
| [select](#panel.Card.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, design, height, min_width, min_height, max_width,
> max_height, margin, styles, stylesheets, tags, width, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.layout.base.ListLike"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListLike](panel.layout.base.md#panel.layout.base.ListLike):
> objects
>
> [class="reference internal" title="panel.layout.base.ListPanel"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListPanel](panel.layout.base.md#panel.layout.base.ListPanel):
> scroll
>
> [class="reference internal" title="panel.layout.base.Column"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.Column](panel.layout.base.md#panel.layout.base.Column):
> auto_scroll_limit, scroll_button_threshold, scroll_position,
> view_latest
>
>

`css_classes`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=['card'],`` ``item_type=<class`` ``'str'>,`` ``label='Css`` ``classes',`` ``nested_refs=True)`
CSS classes to apply to the overall Card.

`active_header_background`` ``=`` ``String(allow_None=True,`` ``label='Active`` ``header`` ``background')`
A valid CSS color for the header background when not collapsed.

`button_css_classes`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=['card-button'],`` ``label='Button`` ``css`` ``classes')`
CSS classes to apply to the button element.

`collapsible`` ``=`` ``Boolean(default=True,`` ``label='Collapsible')`
Whether the Card should be expandable and collapsible.

`collapsed`` ``=`` ``Boolean(default=False,`` ``label='Collapsed')`
Whether the contents of the Card are collapsed.

`header`` ``=`` ``Child(allow_None=True,`` ``class_=<class`` ``'panel.viewable.Viewable'>,`` ``label='Header')`
A Panel component to display in the header bar of the Card. Will
override the given title if defined.

`header_background`` ``=`` ``String(default='',`` ``label='Header`` ``background')`
A valid CSS color for the header background.

`header_color`` ``=`` ``String(default='',`` ``label='Header`` ``color')`
A valid CSS color to apply to the header text.

`header_css_classes`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=['card-header'],`` ``label='Header`` ``css`` ``classes')`
CSS classes to apply to the header element.

`hide_header`` ``=`` ``Boolean(default=False,`` ``label='Hide`` ``header')`
Whether to skip rendering the header.

`title_css_classes`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=['card-title'],`` ``label='Title`` ``css`` ``classes')`
CSS classes to apply to the header title.

`title`` ``=`` ``String(default='',`` ``label='Title')`
A title to be displayed in the Card header, will be overridden by the
header if defined.

select(selector: type \| Callable\[\[Viewable\], bool\] \| None = None) → list\[Viewable\]
Iterates over the Viewable and any potential children in the applying
the Selector.

Parameters:
**selector: type or callable or None**
The selector allows selecting a subset of Viewables by declaring a type
or callable function to filter by.

Returns:
viewables: list(Viewable)

class panel.Column(\*objects: Any, **params: Any)
Bases: [ListPanel](panel.layout.base.md#panel.layout.base.ListPanel)

The Column layout allows arranging multiple panel objects in a vertical
container.

It has a list-like API with methods to append, extend, clear, insert,
pop, remove and \_\_setitem\_\_, which makes it possible to
interactively update and modify the layout.

Reference:
[https://panel.holoviz.org/reference/layouts/Column.html](https://panel.holoviz.org/reference/layouts/Column.html)

Example:

\>\>\>
pn.Column(some_widget,
some_pane,
some_python_object)

Methods

|  |  |
|----|----|
| [scroll_to](#panel.Column.scroll_to)(index) | Scrolls to the child at the provided index. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, margin, styles, stylesheets, tags,
> width, width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.layout.base.ListLike"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListLike](panel.layout.base.md#panel.layout.base.ListLike):
> objects
>
> [class="reference internal" title="panel.layout.base.ListPanel"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListPanel](panel.layout.base.md#panel.layout.base.ListPanel):
> scroll
>
>

`auto_scroll_limit`` ``=`` ``Integer(bounds=(0,`` ``None),`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Auto`` ``scroll`` ``limit')`
Max pixel distance from the latest object in the Column to activate
automatic scrolling upon update. Setting to 0 disables auto-scrolling.

`scroll_button_threshold`` ``=`` ``Integer(bounds=(0,`` ``None),`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Scroll`` ``button`` ``threshold')`
Min pixel distance from the latest object in the Column to display the
scroll button. Setting to 0 disables the scroll button.

`scroll_position`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Scroll`` ``position')`
Current scroll position of the Column. Setting this value will update
the scroll position of the Column. Setting to 0 will scroll to the top.

`view_latest`` ``=`` ``Boolean(default=False,`` ``label='View`` ``latest')`
Whether to scroll to the latest object on init. If not enabled the view
will be on the first object.

scroll_to(index: int)
Scrolls to the child at the provided index.

Parameters:
**index: int**
Index of the child object to scroll to.

class panel.Feed(\*objects, **params)
Bases: [Column](panel.layout.base.md#panel.layout.base.Column)

The Feed class inherits from the Column layout, thereby enabling the
arrangement of multiple panel objects within a vertical container.
However, it restrictively manages the number of objects displayed at any
moment. This layout is particularly useful for efficiently rendering a
substantial number of objects.

Similar to Column, the Feed provides a list-like API, including methods
such as append, extend, clear, insert, pop, remove, and \_\_setitem\_\_.
These methods facilitate interactive updates and modifications to the
layout.

Reference:
[https://panel.holoviz.org/reference/layouts/Feed.html](https://panel.holoviz.org/reference/layouts/Feed.html)

Example:

\>\>\>
pn.Feed(some_widget,
some_pane,
some_python_object,
...,
python_object_1002)

Methods

|  |  |
|----|----|
| [scroll_to_latest](#panel.Feed.scroll_to_latest)(\[scroll_limit\]) | Scrolls the Feed to the latest entry. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, margin, styles, stylesheets, tags,
> width, width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.layout.base.ListLike"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListLike](panel.layout.base.md#panel.layout.base.ListLike):
> objects
>
> [class="reference internal" title="panel.layout.base.Column"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.Column](panel.layout.base.md#panel.layout.base.Column):
> auto_scroll_limit, scroll_button_threshold, scroll_position,
> view_latest
>
>

`scroll`` ``=`` ``Selector(default='y',`` ``label='Scroll',`` ``names={},`` ``objects=[False,`` ``True,`` ``'both-auto',`` ``'y-auto',`` ``'x-auto',`` ``'both',`` ``'x',`` ``'y'])`
Whether to add scrollbars if the content overflows the size of the
container. If “both-auto”, will only add scrollbars if the content
overflows in either directions. If “x-auto” or “y-auto”, will only add
scrollbars if the content overflows in the respective direction. If
“both”, will always add scrollbars. If “x” or “y”, will always add
scrollbars in the respective direction. If False, overflowing content
will be clipped. If True, will only add scrollbars in the direction of
the container, (e.g. Column: vertical, Row: horizontal).

`load_buffer`` ``=`` ``Integer(bounds=(0,`` ``None),`` ``default=50,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Load`` ``buffer')`
The number of objects loaded on each side of the visible objects. When
scrolled halfway into the buffer, the feed will automatically load
additional objects while unloading objects on the opposite side.

`visible_range`` ``=`` ``Range(allow_None=True,`` ``constant=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Visible`` ``range',`` ``length=2,`` ``readonly=True)`
Read-only upper and lower bounds of the currently visible feed objects.
This list is automatically updated based on scrolling.

scroll_to_latest(scroll_limit: float \| None = None) → None
Scrolls the Feed to the latest entry.

Parameters:
scroll_limit : float, optional
Maximum pixel distance from the latest object in the Feed to trigger
scrolling. If the distance exceeds this limit, scrolling will not occur.
If this is not set, it will always scroll to the latest while setting
this to 0 disables scrolling.

class panel.FlexBox(\*objects, **params)
Bases: [ListLike](panel.layout.base.md#panel.layout.base.ListLike),
[ReactiveHTML](panel.reactive.md#panel.reactive.ReactiveHTML)

The FlexBox is a list-like layout (unlike GridSpec) that wraps objects
into a CSS flex container.

It has a list-like API with methods to append, extend, clear, insert,
pop, remove and \_\_setitem\_\_, which makes it possible to
interactively update and modify the layout. It exposes all the CSS
options for controlling the behavior and layout of the flex box.

Reference:
[https://panel.holoviz.org/reference/layouts/FlexBox.html](https://panel.holoviz.org/reference/layouts/FlexBox.html)

Example:

\>\>\>
pn.FlexBox(
...
some_python_object,
another_python_object,
..., ...
 the_last_python_object
... )

Methods

|  |  |
|----|----|
| [clone](#panel.FlexBox.clone)(\*objects, **params) | Makes a copy of the layout sharing the same parameters. |
| [select](#panel.FlexBox.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, margin, styles, stylesheets, tags,
> width, width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.layout.base.ListLike"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListLike](panel.layout.base.md#panel.layout.base.ListLike):
> objects
>
>

`align_content`` ``=`` ``Selector(default='flex-start',`` ``label='Align`` ``content',`` ``names={},`` ``objects=['normal',`` ``'flex-start',`` ``'flex-end',`` ``'center',`` ``'space-between',`` ``'space-around',`` ``'space-evenly',`` ``'stretch',`` ``'start',`` ``'end',`` ``'baseline',`` ``'first`` ``baseline',`` ``'last`` ``baseline'])`
Defines how a flex container’s lines align when there is extra space in
the cross-axis.

`align_items`` ``=`` ``Selector(default='flex-start',`` ``label='Align`` ``items',`` ``names={},`` ``objects=['stretch',`` ``'flex-start',`` ``'flex-end',`` ``'center',`` ``'baseline',`` ``'first`` ``baseline',`` ``'last`` ``baseline',`` ``'start',`` ``'end',`` ``'self-start',`` ``'self-end'])`
Defines the default behavior for how flex items are laid out along the
cross axis on the current line.

`flex_direction`` ``=`` ``Selector(default='row',`` ``label='Flex`` ``direction',`` ``names={},`` ``objects=['row',`` ``'row-reverse',`` ``'column',`` ``'column-reverse'])`
This establishes the main-axis, thus defining the direction flex items
are placed in the flex container.

`flex_wrap`` ``=`` ``Selector(default='wrap',`` ``label='Flex`` ``wrap',`` ``names={},`` ``objects=['nowrap',`` ``'wrap',`` ``'wrap-reverse'])`
Whether and how to wrap items in the flex container.

`gap`` ``=`` ``String(default='',`` ``label='Gap')`
Defines the spacing between flex items, supporting various units (px,
em, rem, %, vw/vh).

`justify_content`` ``=`` ``Selector(default='flex-start',`` ``label='Justify`` ``content',`` ``names={},`` ``objects=['flex-start',`` ``'flex-end',`` ``'center',`` ``'space-between',`` ``'space-around',`` ``'space-evenly',`` ``'start',`` ``'end',`` ``'left',`` ``'right'])`
Defines the alignment along the main axis.

clone(\*objects: t.Any, **params: t.Any) → Self
Makes a copy of the layout sharing the same parameters.

Parameters:
**objects: Objects to add to the cloned layout.**

**params: Keyword arguments override the parameters on the clone.**

Returns:
Cloned layout object

select(selector=None)
Iterates over the Viewable and any potential children in the applying
the Selector.

Parameters:
**selector: type or callable or None**
The selector allows selecting a subset of Viewables by declaring a type
or callable function to filter by.

Returns:
viewables: list(Viewable)

class panel.FloatPanel(\*objects, name='', **params)
Bases: [ListLike](panel.layout.base.md#panel.layout.base.ListLike),
[ReactiveHTML](panel.reactive.md#panel.reactive.ReactiveHTML)

Float provides a floating panel layout.

Reference:
[https://panel.holoviz.org/reference/layouts/FloatPanel.html](https://panel.holoviz.org/reference/layouts/FloatPanel.html)

Example:

\>\>\>
import
panel
as
pn \>\>\>
pn.extension("floatpanel")
\>\>\>
pn.layout.FloatPanel("**I
can float**!",
position="center",
width=300).servable()

Methods

|  |  |
|----|----|
| [clone](#panel.FloatPanel.clone)(\*objects, **params) | Makes a copy of the layout sharing the same parameters. |
| [select](#panel.FloatPanel.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, margin, styles, stylesheets, tags,
> width, width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.layout.base.ListLike"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListLike](panel.layout.base.md#panel.layout.base.ListLike):
> objects
>
>

`config`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Config')`
Additional jsPanel configuration with precedence over parameter values.

`contained`` ``=`` ``Boolean(default=True,`` ``label='Contained')`
Whether the component is contained within parent container or completely
free floating.

`position`` ``=`` ``Selector(default='right-top',`` ``label='Position',`` ``names={},`` ``objects=['center',`` ``'left-top',`` ``'center-top',`` ``'right-top',`` ``'right-center',`` ``'right-bottom',`` ``'center-bottom',`` ``'left-bottom',`` ``'left-center'])`
The initial position if the container is free-floating.

`offsetx`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Offsetx')`
Horizontal offset in pixels.

`offsety`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Offsety')`
Vertical offset in pixels.

`theme`` ``=`` ``String(default='primary',`` ``label='Theme')`
The theme which can be one of: - Built-ins: ‘default’, ‘primary’,
‘secondary’, ‘info’, ‘success’, ‘warning’, ‘danger’, ‘light’, ‘dark’ and
‘none’ - HEX, RGB and HSL color values like ‘#123456’ Any standardized
color name like ‘forestgreen’ and color names from the Material Design
Color System like ‘purple900’ - Additionally a theme string may include
one of the modifiers ‘filled’, ‘filledlight’, ‘filleddark’ or
‘fillcolor’ separated from the theme color by a space like ‘primary

`status`` ``=`` ``Selector(default='normalized',`` ``label='Status',`` ``names={},`` ``objects=['normalized',`` ``'maximized',`` ``'minimized',`` ``'smallified',`` ``'smallifiedmax',`` ``'closed'])`
The current status of the panel.

clone(\*objects: t.Any, **params: t.Any) → Self
Makes a copy of the layout sharing the same parameters.

Parameters:
**objects: Objects to add to the cloned layout.**

**params: Keyword arguments override the parameters on the clone.**

Returns:
Cloned layout object

select(selector=None)
Iterates over the Viewable and any potential children in the applying
the Selector.

Parameters:
**selector: type or callable or None**
The selector allows selecting a subset of Viewables by declaring a type
or callable function to filter by.

Returns:
viewables: list(Viewable)

class panel.GridBox(\*objects: Any, **params: Any)
Bases: [ListPanel](panel.layout.base.md#panel.layout.base.ListPanel)

The GridBox is a list-like layout (unlike GridSpec) that wraps objects
into a grid according to the specified nrows and ncols parameters.

It has a list-like API with methods to append, extend, clear, insert,
pop, remove and \_\_setitem\_\_, which makes it possible to
interactively update and modify the layout.

Reference:
[https://panel.holoviz.org/reference/layouts/GridBox.html](https://panel.holoviz.org/reference/layouts/GridBox.html)

Example:

\>\>\>
pn.GridBox(
...
python_object_1,
python_object_2,
..., ...
 python_object_24,
ncols=6
... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, margin, styles, stylesheets, tags,
> width, width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.layout.base.ListLike"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListLike](panel.layout.base.md#panel.layout.base.ListLike):
> objects
>
> [class="reference internal" title="panel.layout.base.ListPanel"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListPanel](panel.layout.base.md#panel.layout.base.ListPanel):
> scroll
>
>

`nrows`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Nrows')`
Number of rows to reflow the layout into.

`ncols`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Ncols')`
Number of columns to reflow the layout into.

class panel.GridSpec(\*, mode, ncols, nrows, objects, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, name)
Bases: [Panel](panel.layout.base.md#panel.layout.base.Panel)

The GridSpec is an *array like* layout that allows arranging multiple
Panel objects in a grid using a simple API to assign objects to
individual grid cells or to a grid span.

Other layout containers function like lists, but a GridSpec has an API
similar to a 2D array, making it possible to use 2D assignment to
populate, index, and slice the grid.

See GridStack for a similar layout that allows the user to resize and
drag the cells.

Reference:
[https://panel.holoviz.org/reference/layouts/GridSpec.html](https://panel.holoviz.org/reference/layouts/GridSpec.html)

Example:

\>\>\>
import
panel
as
pn \>\>\>
gspec =
pn.GridSpec(width=800,
height=600)
\>\>\>
gspec\[:,
0 \]
=
pn.Spacer(styles=dict(background='red'))
\>\>\>
gspec\[0,
1:3\]
=
pn.Spacer(styles=dict(background='green'))
\>\>\>
gspec\[1,
2:4\]
=
pn.Spacer(styles=dict(background='orange'))
\>\>\>
gspec\[2,
1:4\]
=
pn.Spacer(styles=dict(background='blue'))
\>\>\>
gspec\[0:1,
3:4\]
=
pn.Spacer(styles=dict(background='purple'))
\>\>\> gspec

Attributes:
**grid**

Methods

|  |  |
|----|----|
| [clone](#panel.GridSpec.clone)(**params) | Makes a copy of the GridSpec sharing the same parameters. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, margin, styles, stylesheets, tags,
> width, width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
>

`objects`` ``=`` ``ChildDict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Objects')`
The dictionary of child objects that make up the grid.

`mode`` ``=`` ``Selector(default='warn',`` ``label='Mode',`` ``names={},`` ``objects=['warn',`` ``'error',`` ``'override'])`
Whether to warn, error or simply override on overlapping assignment.

`ncols`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Ncols')`
Limits the number of columns that can be assigned.

`nrows`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Nrows')`
Limits the number of rows that can be assigned.

clone(**params)
Makes a copy of the GridSpec sharing the same parameters.

Parameters:
**params: Keyword arguments override the parameters on the clone.**

Returns:
Cloned GridSpec object

class panel.GridStack(\*, allow_drag, allow_resize, state, mode, ncols, nrows, objects, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, name)
Bases: [ReactiveHTML](panel.reactive.md#panel.reactive.ReactiveHTML),
[GridSpec](panel.layout.grid.md#panel.layout.grid.GridSpec)

The GridStack layout allows arranging multiple Panel objects in a grid
using a simple API to assign objects to individual grid cells or to a
grid span.

Other layout containers function like lists, but a GridSpec has an API
similar to a 2D array, making it possible to use 2D assignment to
populate, index, and slice the grid.

Reference:
[https://panel.holoviz.org/reference/layouts/GridStack.html](https://panel.holoviz.org/reference/layouts/GridStack.html)

Example:

\>\>\>
pn.extension('gridstack')
\>\>\> gstack
=
GridStack(sizing_mode='stretch_both')
\>\>\>
gstack\[
: ,
0:
3\]
=
pn.Spacer(styles=dict(background='red'))
\>\>\>
gstack\[0:2,
3:
9\]
=
pn.Spacer(styles=dict(background='green'))
\>\>\>
gstack\[2:4,
6:12\]
=
pn.Spacer(styles=dict(background='orange'))
\>\>\>
gstack\[4:6,
3:12\]
=
pn.Spacer(styles=dict(background='blue'))
\>\>\>
gstack\[0:2,
9:12\]
=
pn.Spacer(styles=dict(background='purple'))

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, margin, styles, stylesheets, tags,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.layout.grid.GridSpec"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.grid.GridSpec](panel.layout.grid.md#panel.layout.grid.GridSpec):
> objects, mode, ncols, nrows
>
>

`height`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Height')`
The height of the component (in pixels). This can be either fixed or
preferred height, depending on height sizing policy.

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
The width of the component (in pixels). This can be either fixed or
preferred width, depending on width sizing policy.

`allow_resize`` ``=`` ``Boolean(default=True,`` ``label='Allow`` ``resize')`
Allow resizing the grid cells.

`allow_drag`` ``=`` ``Boolean(default=True,`` ``label='Allow`` ``drag')`
Allow dragging the grid cells.

`state`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'dict'>,`` ``label='State')`
Current state of the grid (updated as items are resized and dragged).

class panel.HSpacer(refs=None, **params)
Bases: [Spacer](panel.layout.spacer.md#panel.layout.spacer.Spacer)

The HSpacer layout provides responsive horizontal spacing.

Using this component we can space objects equidistantly in a layout and
allow the empty space to shrink when the browser is resized.

How-to: [https://panel.holoviz.org/how_to/layout/spacing.html#spacer-components](https://panel.holoviz.org/how_to/layout/spacing.html#spacer-components)

Example:

\>\>\>
pn.Row(
...
pn.layout.HSpacer(),
'Item 1',
...
pn.layout.HSpacer(),
'Item 2',
...
pn.layout.HSpacer()
... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, margin, styles, stylesheets, tags,
> width, width_policy, height_policy, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
>

`sizing_mode`` ``=`` ``Parameter(constant=True,`` ``default='stretch_width',`` ``label='Sizing`` ``mode',`` ``readonly=True)`
How the component should size itself. This is a high-level setting for
maintaining width and height of the component. To gain more fine grained
control over sizing, use `width_policy`,
`height_policy` and
`aspect_ratio` instead (those take precedence
over `sizing_mode`).
`"fixed"` Component is not responsive. It will
retain its original width and height regardless of any subsequent
browser window resize events. `"stretch_width"`
Component will responsively resize to stretch to the available width,
without maintaining any aspect ratio. The height of the component
depends on the type of the component and may be fixed or fit to
component’s contents. `"stretch_height"`
Component will responsively resize to stretch to the available height,
without maintaining any aspect ratio. The width of the component depends
on the type of the component and may be fixed or fit to component’s
contents. `"stretch_both"` Component is
completely responsive, independently in width and height, and will
occupy all the available horizontal and vertical space, even if this
changes the aspect ratio of the component.
`"scale_width"` Component will responsively
resize to stretch to the available width, while maintaining the original
or provided aspect ratio. `"scale_height"`
Component will responsively resize to stretch to the available height,
while maintaining the original or provided aspect ratio.
`"scale_both"` Component will responsively
resize to both the available width and height, while maintaining the
original or provided aspect ratio.

class panel.Modal(\*objects: Any, **params: Any)
Bases: [ListPanel](panel.layout.base.md#panel.layout.base.ListPanel)

Create a modal dialog that can be opened and closed.

Methods

|  |  |
|----|----|
| [create_button](#panel.Modal.create_button)(action, **kwargs) | Create a button to show, hide or toggle the modal. |
| [show](#panel.Modal.show)() | Starts a Bokeh server and displays the Viewable in a new tab. |

|            |     |
|------------|-----|
| **hide**   |     |
| **toggle** |     |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, margin, styles, stylesheets, tags,
> width, width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.layout.base.ListLike"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListLike](panel.layout.base.md#panel.layout.base.ListLike):
> objects
>
> [class="reference internal" title="panel.layout.base.ListPanel"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListPanel](panel.layout.base.md#panel.layout.base.ListPanel):
> scroll
>
>

`open`` ``=`` ``Boolean(default=False,`` ``label='Open')`
Whether to open the modal.

`show_close_button`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``close`` ``button')`
Whether to show a close button in the modal.

`background_close`` ``=`` ``Boolean(default=True,`` ``label='Background`` ``close')`
Whether to enable closing the modal when clicking the background.

create_button(action: Literal\['show', 'hide', 'toggle'\], **kwargs)
Create a button to show, hide or toggle the modal.

show()
Starts a Bokeh server and displays the Viewable in a new tab.

Parameters:
title : str \| None
A string title to give the Document (if served as an app)

**port: int (optional, default=0)**
Allows specifying a specific port

address : str
The address the server should listen on for HTTP requests.

**websocket_origin: str or list(str) (optional)**
A list of hosts that can connect to the websocket. This is typically
required when embedding a server app in an external web site. If None,
“localhost” is used.

**threaded: boolean (optional, default=False)**
Whether to launch the Server on a separate thread, allowing interactive
use.

**verbose: boolean (optional, default=True)**
Whether to print the address and port

open : boolean (optional, default=True)
Whether to open the server in a new browser tab

location : boolean or panel.io.location.Location
Whether to create a Location component to observe and set the URL
location.

Returns:
server: bokeh.server.Server or panel.io.server.StoppableThread
Returns the Bokeh server instance or the thread the server was launched
on (if threaded=True)

class panel.Param(object=None, **params)
Bases: [Pane](panel.pane.base.md#panel.pane.base.Pane)

Param panes render a Parameterized class into a set of interactive
widgets that are dynamically linked to the parameter values of the
class.

Reference:
[https://panel.holoviz.org/reference/panes/Param.html](https://panel.holoviz.org/reference/panes/Param.html)

Example:

\>\>\>
import
param \>\>\>
import
panel
as
pn \>\>\>
pn.extension()

\>\>\>
class
App(param.Parameterized):
\>\>\>  some_text
=
param.String(default="Hello")
\>\>\>  some_float
=
param.Number(default=1,
bounds=(0,
10),
step=0.1)
\>\>\>  some_boolean
=
param.Boolean(default=True)

\>\>\> app
=
App()

\>\>\>
pn.Param(app,
parameters=\["some_text",
"some_float"\],
show_name=False).servable()

Attributes:
**widgets**

Methods

|  |  |
|----|----|
| [applies](#panel.Param.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |
| [get_root](#panel.Param.get_root)(\[doc, comm, preprocess\]) | Returns the root model and applies pre-processing hooks |
| [select](#panel.Param.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |
| [widget](#panel.Param.widget)(p_name\[, parameterized, widget_spec\]) | Get widget for param_name |

|                 |     |
|-----------------|-----|
| **widget_type** |     |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin
>
>

`height`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Height')`
Height of widgetbox the parameter widgets are displayed in.

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
Width of widgetbox the parameter widgets are displayed in.

`default_layout`` ``=`` ``ClassSelector(class_=(<class`` ``'panel.layout.base.ListLike'>,`` ``<class`` ``'panel.layout.base.NamedListLike'>),`` ``default=<class`` ``'panel.layout.base.Column'>,`` ``label='Default`` ``layout')`
Defines the layout the model(s) returned by the pane will be placed in.

`object`` ``=`` ``Parameter(allow_None=True,`` ``label='Object')`
The object being wrapped, which will be converted to a Bokeh model.

`display_threshold`` ``=`` ``Number(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Display`` ``threshold')`
Parameters with precedence below this value are not displayed.

`default_precedence`` ``=`` ``Number(default=1e-08,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Default`` ``precedence')`
Precedence value to use for parameters with no declared precedence. By
default, zero predecence is available for forcing some parameters to the
top of the list, and other values above the default_precedence values
can be used to sort or group parameters arbitrarily.

`expand`` ``=`` ``Boolean(default=False,`` ``label='Expand')`
Whether parameterized subobjects are expanded or collapsed on
instantiation.

`expand_button`` ``=`` ``Boolean(allow_None=True,`` ``label='Expand`` ``button')`
Whether to add buttons to expand and collapse sub-objects.

`expand_layout`` ``=`` ``Parameter(default=<class`` ``'panel.layout.base.Column'>,`` ``label='Expand`` ``layout')`
Layout to expand sub-objects into.

`hide_constant`` ``=`` ``Boolean(default=False,`` ``label='Hide`` ``constant')`
Whether to hide widgets of constant parameters.

`initializer`` ``=`` ``Callable(allow_None=True,`` ``label='Initializer')`
User-supplied function that will be called on initialization, usually to
update the default Parameter values of the underlying parameterized
object.

`parameters`` ``=`` ``List(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'str'>,`` ``label='Parameters')`
If set this serves as a allowlist of parameters to display on the
supplied Parameterized object.

`show_labels`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``labels')`
Whether to show labels for each widget

`show_name`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``name')`
Whether to show the parameterized object’s name

`sort`` ``=`` ``ClassSelector(class_=(<class`` ``'bool'>,`` ``<class`` ``'collections.abc.Callable'>),`` ``default=False,`` ``label='Sort')`
If True the widgets will be sorted alphabetically by label. If a
callable is provided it will be used to sort the Parameters, for example
lambda x: x\[1\].label\[::-1\] will sort by the reversed label.

`widgets`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``label='Widgets')`
Dictionary of widget overrides, mapping from parameter name to widget
class.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

default_layout
alias of [Column](panel.layout.base.md#panel.layout.base.Column)

expand_layout
alias of [Column](panel.layout.base.md#panel.layout.base.Column)

get_root(doc: Document \| None = None, comm: Comm \| None = None, preprocess: bool = True) → Model
Returns the root model and applies pre-processing hooks

Parameters:
**doc: bokeh.document.Document**
Optional Bokeh document the bokeh model will be attached to.

**comm: pyviz_comms.Comm**
Optional pyviz_comms when working in notebook

**preprocess: bool (default=True)**
Whether to run preprocessing hooks

Returns:
Returns the bokeh model corresponding to this panel object

select(selector=None)
Iterates over the Viewable and any potential children in the applying
the Selector.

Parameters:
**selector: type or callable or None**
The selector allows selecting a subset of Viewables by declaring a type
or callable function to filter by.

Returns:
viewables: list(Viewable)

widget(p_name: str, parameterized: Parameterized \| None = None, widget_spec: type\[WidgetBase\] \| dict \| None = None)
Get widget for param_name

class panel.ReactiveExpr(object=None, **params)
Bases: [Pane](panel.pane.base.md#panel.pane.base.Pane)

ReactiveExpr generates a UI for param.rx objects by rendering the
widgets and outputs.

Attributes:
**widgets**

Methods

|  |  |
|----|----|
| [applies](#panel.ReactiveExpr.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout
>
>

`object`` ``=`` ``Parameter(allow_None=True,`` ``label='Object')`
The object being wrapped, which will be converted to a Bokeh model.

`center`` ``=`` ``Boolean(default=False,`` ``label='Center')`
Whether to center the output.

`show_widgets`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``widgets')`
Whether to display the widget inputs.

`widget_layout`` ``=`` ``ClassSelector(class_=<class`` ``'panel.layout.base.ListLike'>,`` ``constant=True,`` ``default=<class`` ``'panel.layout.base.WidgetBox'>,`` ``label='Widget`` ``layout')`
The layout object to display the widgets in.

`widget_location`` ``=`` ``Selector(default='left_top',`` ``label='Widget`` ``location',`` ``names={},`` ``objects=['left',`` ``'right',`` ``'top',`` ``'bottom',`` ``'top_left',`` ``'top_right',`` ``'bottom_left',`` ``'bottom_right',`` ``'left_top',`` ``'right_top',`` ``'right_bottom'])`
The location of the widgets relative to the output of the reactive
expression.

classmethod applies(object)
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

widget_layout
alias of [WidgetBox](panel.layout.base.md#panel.layout.base.WidgetBox)

class panel.Row(\*objects: Any, **params: Any)
Bases: [ListPanel](panel.layout.base.md#panel.layout.base.ListPanel)

The Row layout allows arranging multiple panel objects in a horizontal
container.

It has a list-like API with methods to append, extend, clear, insert,
pop, remove and \_\_setitem\_\_, which makes it possible to
interactively update and modify the layout.

Reference:
[https://panel.holoviz.org/reference/layouts/Row.html](https://panel.holoviz.org/reference/layouts/Row.html)

Example:

\>\>\>
pn.Row(some_widget,
some_pane,
some_python_object)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, margin, styles, stylesheets, tags,
> width, width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.layout.base.ListLike"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListLike](panel.layout.base.md#panel.layout.base.ListLike):
> objects
>
> [class="reference internal" title="panel.layout.base.ListPanel"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListPanel](panel.layout.base.md#panel.layout.base.ListPanel):
> scroll
>
>

class panel.Spacer(refs=None, **params)
Bases: [Reactive](panel.reactive.md#panel.reactive.Reactive)

The Spacer layout is a very versatile component which makes it easy to
put fixed or responsive spacing between objects.

Like all other components spacers support both absolute and responsive
sizing modes.

How-to: [https://panel.holoviz.org/how_to/layout/spacing.html#spacer-components](https://panel.holoviz.org/how_to/layout/spacing.html#spacer-components)

Example:

\>\>\>
pn.Row(
...
1,
pn.Spacer(width=200),
...
2,
pn.Spacer(width=100),
...  3
... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, margin, styles, stylesheets, tags,
> width, width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
>

class panel.Swipe(\*objects, **params)
Bases: [ListLike](panel.layout.base.md#panel.layout.base.ListLike),
[ReactiveHTML](panel.reactive.md#panel.reactive.ReactiveHTML)

The Swipe layout enables you to quickly compare two panels laid out on
top of each other with a part of the *before* panel shown on one side of
a slider and a part of the *after* panel shown on the other side.

Attributes:
**after**

**before**

Methods

|  |  |
|----|----|
| [clone](#panel.Swipe.clone)(\*objects, **params) | Makes a copy of the layout sharing the same parameters. |
| [select](#panel.Swipe.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, margin, styles, stylesheets, tags,
> width, width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
>

`objects`` ``=`` ``Children(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'panel.viewable.Viewable'>,`` ``label='Objects')`
The list of child objects that make up the layout.

`slider_width`` ``=`` ``Integer(bounds=(0,`` ``25),`` ``default=5,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Slider`` ``width')`
The width of the slider in pixels

`slider_color`` ``=`` ``Color(allow_named=True,`` ``default='black',`` ``label='Slider`` ``color')`
The color of the slider

`start`` ``=`` ``Integer(bounds=(0,`` ``100),`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start')`
Limits the minimum percentage the swipe handler can be moved to.

`end`` ``=`` ``Integer(bounds=(0,`` ``100),`` ``default=100,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End')`
Limits the maximum percentage the swipe handler can be moved to.

`value`` ``=`` ``Integer(bounds=(0,`` ``100),`` ``default=50,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
The percentage of the *after* panel to show.

`_before`` ``=`` ``Parameter(allow_None=True,`` ``label='`` ``before')`

`_after`` ``=`` ``Parameter(allow_None=True,`` ``label='`` ``after')`

clone(\*objects: t.Any, **params: t.Any) → Self
Makes a copy of the layout sharing the same parameters.

Parameters:
**objects: Objects to add to the cloned layout.**

**params: Keyword arguments override the parameters on the clone.**

Returns:
Cloned layout object

select(selector=None)
Iterates over the Viewable and any potential children in the applying
the Selector.

Parameters:
**selector: type or callable or None**
The selector allows selecting a subset of Viewables by declaring a type
or callable function to filter by.

Returns:
viewables: list(Viewable)

class panel.Tabs(\*objects, **params)
Bases: [NamedListPanel](panel.layout.base.md#panel.layout.base.NamedListPanel)

The Tabs layout allows switching between multiple objects by clicking on
the corresponding tab header.

Tab labels may be defined explicitly as part of a tuple or will be
inferred from the name parameter of the tab’s contents.

Like Column and Row, Tabs has a list-like API with methods to append,
extend, clear, insert, pop, remove and \_\_setitem\_\_, which make it
possible to interactively update and modify the tabs.

Reference:
[https://panel.holoviz.org/reference/layouts/Tabs.html](https://panel.holoviz.org/reference/layouts/Tabs.html)

Example:

\>\>\>
pn.Tabs(('Scatter',
plot1),
some_pane_with_a_name)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, margin, styles, stylesheets, tags,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.layout.base.NamedListLike"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.NamedListLike](panel.layout.base.md#panel.layout.base.NamedListLike):
> objects
>
> [class="reference internal"
> title="panel.layout.base.NamedListPanel"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.NamedListPanel](panel.layout.base.md#panel.layout.base.NamedListPanel):
> active, scroll
>
>

`height`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Height')`
The height of the component (in pixels). This can be either fixed or
preferred height, depending on height sizing policy.

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
The width of the component (in pixels). This can be either fixed or
preferred width, depending on width sizing policy.

`closable`` ``=`` ``Boolean(default=False,`` ``label='Closable')`
Whether it should be possible to close tabs.

`dynamic`` ``=`` ``Boolean(default=False,`` ``label='Dynamic')`
Dynamically populate only the active tab.

`tabs_location`` ``=`` ``Selector(default='above',`` ``label='Tabs`` ``location',`` ``names={},`` ``objects=['above',`` ``'below',`` ``'left',`` ``'right'])`
The location of the tabs relative to the tab contents.

class panel.Template(template: str \| \_Template, nb_template: str \| \_Template \| None = None, items: dict\[str, t.Any\] \| None = None, **params)
Bases:
[BaseTemplate](panel.template.base.md#panel.template.base.BaseTemplate)

A Template is a high-level component to render multiple Panel objects
into a single HTML document defined through a Jinja2 template. The
Template object is given a Jinja2 template and then allows populating
this template by adding Panel objects, which are given unique names.
These unique names may then be referenced in the template to insert the
rendered Panel object at a specific location. For instance, given a
Jinja2 template that defines roots A and B like this:

>
>
> \<div\> {{ embed(roots.A) }} \</div\> \<div\> {{ embed(roots.B) }}
> \</div\>
>
>

We can then populate the template by adding panel ‘A’ and ‘B’ to the
Template object:

>
>
> template.add_panel(‘A’, pn.panel(‘A’)) template.add_panel(‘B’,
> pn.panel(‘B’))
>
>

Once a template has been fully populated it can be rendered using the
same API as other Panel objects. Note that all roots that have been
declared using the {{ embed(roots.A) }} syntax in the Jinja2 template
must be defined when rendered.

Since embedding complex CSS frameworks inside a notebook can have
undesirable side-effects and a notebook does not afford the same amount
of screen space a Template may given separate template and nb_template
objects. This allows for different layouts when served as a standalone
server and when used in the notebook.

Methods

|  |  |
|----|----|
| [add_panel](#panel.Template.add_panel)(name, panel\[, tags\]) | Add panels to the Template, which may then be referenced by the given name using the jinja2 embed macro. |
| [add_variable](#panel.Template.add_variable)(name, value) | Add parameters to the template, which may then be referenced by the given name in the Jinja2 template. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal"
> title="panel.template.base.BaseTemplate"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.base.BaseTemplate](panel.template.base.md#panel.template.base.BaseTemplate):
> config, design, location, theme
>
>

add_panel(name: str, panel: Any, tags: list\[str\] = \[\]) → None
Add panels to the Template, which may then be referenced by the given
name using the jinja2 embed macro.

Parameters:
name : str
The name to refer to the panel by in the template

panel : panel.Viewable
A Panel component to embed in the template.

add_variable(name: str, value: Any) → None
Add parameters to the template, which may then be referenced by the
given name in the Jinja2 template.

Parameters:
name : str
The name to refer to the panel by in the template

value : object
Any valid Jinja2 variable type.

class panel.VSpacer(refs=None, **params)
Bases: [Spacer](panel.layout.spacer.md#panel.layout.spacer.Spacer)

The VSpacer layout provides responsive vertical spacing.

Using this component we can space objects equidistantly in a layout and
allow the empty space to shrink when the browser is resized.

Reference: [https://panel.holoviz.org/how_to/layout/spacing.html#spacer-components](https://panel.holoviz.org/how_to/layout/spacing.html#spacer-components)

Example:

\>\>\>
pn.Column(
...
pn.layout.VSpacer(),
'Item 1',
...
pn.layout.VSpacer(),
'Item 2',
...
pn.layout.VSpacer()
... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, margin, styles, stylesheets, tags,
> width, width_policy, height_policy, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
>

`sizing_mode`` ``=`` ``Parameter(constant=True,`` ``default='stretch_height',`` ``label='Sizing`` ``mode',`` ``readonly=True)`
How the component should size itself. This is a high-level setting for
maintaining width and height of the component. To gain more fine grained
control over sizing, use `width_policy`,
`height_policy` and
`aspect_ratio` instead (those take precedence
over `sizing_mode`).
`"fixed"` Component is not responsive. It will
retain its original width and height regardless of any subsequent
browser window resize events. `"stretch_width"`
Component will responsively resize to stretch to the available width,
without maintaining any aspect ratio. The height of the component
depends on the type of the component and may be fixed or fit to
component’s contents. `"stretch_height"`
Component will responsively resize to stretch to the available height,
without maintaining any aspect ratio. The width of the component depends
on the type of the component and may be fixed or fit to component’s
contents. `"stretch_both"` Component is
completely responsive, independently in width and height, and will
occupy all the available horizontal and vertical space, even if this
changes the aspect ratio of the component.
`"scale_width"` Component will responsively
resize to stretch to the available width, while maintaining the original
or provided aspect ratio. `"scale_height"`
Component will responsively resize to stretch to the available height,
while maintaining the original or provided aspect ratio.
`"scale_both"` Component will responsively
resize to both the available width and height, while maintaining the
original or provided aspect ratio.

class panel.WidgetBox(\*objects: Any, **params: Any)
Bases: [ListPanel](panel.layout.base.md#panel.layout.base.ListPanel)

The WidgetBox layout allows arranging multiple panel objects in a
vertical (or horizontal) container.

It is largely identical to the Column layout, but has some default
styling that makes widgets be clearly grouped together visually.

It has a list-like API with methods to append, extend, clear, insert,
pop, remove and \_\_setitem\_\_, which make it possible to interactively
update and modify the layout.

Reference:
[https://panel.holoviz.org/reference/layouts/WidgetBox.html](https://panel.holoviz.org/reference/layouts/WidgetBox.html)

Example:

\>\>\>
pn.WidgetBox(some_widget,
another_widget)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, design, height, min_width, min_height, max_width,
> max_height, margin, styles, stylesheets, tags, width, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.layout.base.ListLike"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListLike](panel.layout.base.md#panel.layout.base.ListLike):
> objects
>
> [class="reference internal" title="panel.layout.base.ListPanel"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListPanel](panel.layout.base.md#panel.layout.base.ListPanel):
> scroll
>
>

`css_classes`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=['panel-widget-box'],`` ``item_type=<class`` ``'str'>,`` ``label='Css`` ``classes',`` ``nested_refs=True)`
CSS classes to apply to the layout.

`disabled`` ``=`` ``Boolean(default=False,`` ``label='Disabled')`
Whether the widget is disabled.

`horizontal`` ``=`` ``Boolean(default=False,`` ``label='Horizontal')`
Whether to lay out the widgets in a Row layout as opposed to a Column
layout.

panel.bind(function: Callable\[\[...\], Any\], \*args: Any, watch: bool = False, **kwargs: Any) → Callable\[\[...\], Any\]
Bind constant values, parameters, bound functions or reactive
expressions to a function.

This function creates a wrapper around the given
`function`, binding some or all of its
arguments to constant values, `Parameter`
objects, or reactive expressions. The resulting function automatically
reflects updates to any bound parameters or reactive expressions,
ensuring that its output remains up-to-date.

Similar to `functools.partial()`, arguments can
also be bound to constants, leaving a simple callable object. When
`watch=True`, the function is automatically
evaluated whenever any bound parameter or reactive expression changes.

Parameters:
function : callable, generator, async generator, or coroutine
The function or coroutine to bind constant, dynamic, or reactive
arguments to. It can be:

- A standard callable (e.g., a regular function).

- A generator function (producing iterables).

- An async generator function (producing asynchronous iterables).

- A coroutine function (producing awaitables).

\*args : object, Parameter, bound function or reactive expression rx
Positional arguments to bind to the function. These can be constants,
param.Parameter objects, bound functions or reactive expressions.

watch : bool, optional
If True, the function is automatically evaluated whenever a bound
parameter or reactive expression changes. Defaults to False.

**kwargs : object, Parameter, bound function or reactive expression rx
Keyword arguments to bind to the function. These can also be constants,
param.Parameter objects, bound functions or reactive expressions.

Returns:
callable, generator, async generator, or coroutine
A new function with the bound arguments, annotated with all
dependencies. The function reflects changes to bound parameters or
reactive expressions.

Examples

Bind parameters to a function:

\>\>\>
import
param \>\>\>
class
Example(param.Parameterized):
...  a
=
param.Number(1)
...  b
=
param.Number(2)
\>\>\> example
=
Example()
\>\>\>
def
add(a,
b): ...
 return a
+ b
\>\>\> bound_add
=
param.bind(add,
example.param.a,
example.param.b)
\>\>\>
bound_add()
3

Update a parameter and observe the updated result:

\>\>\>
example.a
= 5
\>\>\>
bound_add()
7

Automatically evaluate the function when bound arguments change:

\>\>\> bound_watch
=
param.bind(print,
example.param.a,
example.param.b,
watch=True)
\>\>\>
example.a
= 1 \#
Triggers automatic evaluation 1 2

panel.cache(func: Callable\[\_P, \_R\] \| None = None, hash_funcs: dict\[type\[t.Any\], Callable\[\[t.Any\], bytes\]\] \| None = None, max_items: int \| None = None, policy: t.Literal\['FIFO', 'LRU', 'LFU'\] = 'LRU', ttl: float \| None = None, to_disk: bool = False, cache_path: str \| os.PathLike \| None = None, per_session: bool = False) → \_CachedFunc\[Callable\[\_P, \_R\]\] \| Callable\[\[Callable\[\_P, \_R\]\], \_CachedFunc\[Callable\[\_P, \_R\]\]\]
Memoizes functions for a user session. Can be used as function
annotation or just directly.

For global caching across user sessions use pn.state.as_cached.

Parameters:
**func: callable**
The function to cache.

**hash_funcs: dict or None**
A dictionary mapping from a type to a function which returns a hash for
an object of that type. If provided this will override the default
hashing function provided by Panel.

**max_items: int or None**
The maximum items to keep in the cache. Default is None, which does not
limit number of items stored in the cache.

**policy: str**
A caching policy when max_items is set, must be one of:
- FIFO: First in - First out

- LRU: Least recently used

- LFU: Least frequently used

**ttl: float or None**
The number of seconds to keep an item in the cache, or None if the cache
should not expire. The default is None.

**to_disk: bool**
Whether to cache to disk using diskcache.

**cache_path: str**
Directory to cache to on disk (if not provided default will be inherited
from config.cache_path).

**per_session: bool**
Whether to cache data only for the current session.

panel.depends(\*dependencies: Dependency \| Callable\[t.Concatenate\[\_S, \_P\], \_R\], watch: bool = False, on_init: bool = False, **kw: Dependency) → DependsFunc\[\_P, \_R\] \| Callable\[\[Callable\[t.Concatenate\[\_S, \_P\], \_R\]\], DependsFunc\[\_P, \_R\]\]
Annotates a function or `Parameterized` method
to express its dependencies.

The specified dependencies can be either be
`Parameter` instances or if a method is
supplied they can be defined as strings referring to Parameters of the
class, or Parameters of subobjects (Parameterized objects that are
values of this object’s parameters). Dependencies can either be on
Parameter values, or on other metadata about the Parameter.

Parameters:
watch : bool, optional
Whether to invoke the function/method when the dependency is updated, by
default `False`.

on_init : bool, optional
Whether to invoke the function/method when the instance is created, by
default `False`.

panel.extension
alias of [panel_extension](panel.config.md#panel.config.panel_extension)

panel.ipywidget(obj: Any, doc=None, **kwargs: Any)
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

panel.panel(obj: Any, **kwargs) → Viewable \| ServableMixin
Creates a displayable Panel object given any valid Python object.

The appropriate Pane to render a specific object is determined by
iterating over all defined Pane types and querying it’s .applies method
for a priority value.

Any keyword arguments are passed down to the applicable Pane.

Setting loading_indicator=True will display a loading indicator while
the function is being evaluated.

To lazily render components when the application loads, you may also
provide a Python function, with or without bound parameter dependencies
and set defer_load=True.

Reference: [https://panel.holoviz.org/explanation/components/components_overview.html#panes](https://panel.holoviz.org/explanation/components/components_overview.html#panes)

\>\>\>
pn.panel(some_python_object,
width=500)

Parameters:
**obj: object**
Any object to be turned into a Panel

****kwargs: dict**
Any keyword arguments to be passed to the applicable Pane

Returns:
layout: Viewable
A Viewable representation of the input object

class panel.rx(obj=None, **kwargs)
Bases: `object`

A class for creating reactive expressions by wrapping objects.

The `rx` class allows you to wrap objects and
operate on them interactively, recording any operations applied. These
recorded operations form a pipeline that can be replayed dynamically
when an operand changes. This makes `rx`
particularly useful for building reactive workflows, such as real-time
data processing or dynamic user interfaces.

Parameters:
obj : any
The object to wrap, such as a number, string, list, or any supported
data structure.

References

For more details, see the user guide:
[https://param.holoviz.org/user_guide/Reactive_Expressions.html](https://param.holoviz.org/user_guide/Reactive_Expressions.html)

Examples

Instantiate
[rx](#panel.rx)
from an object:

\>\>\>
from
param
import rx
\>\>\> reactive_float
=
rx(3.14)

Perform operations on the reactive object:

\>\>\> reactive_result
= reactive_float
\* 2
\>\>\>
reactive_result.value
6.28

Update the original value and see the updated result:

\>\>\>
reactive_float.value
= 1
\>\>\>
reactive_result.rx.value
2

Create a reactive list and compute its length reactively:

\>\>\> reactive_list
=
rx(\[1,
2,
3\])
\>\>\> reactive_length
=
reactive_list.rx.len()
\>\>\>
reactive_length.rx.value
3

classmethod register_accessor(name: str, accessor: Callable\[\[Any\], Any\], predicate: Callable\[\[Any\], bool\] \| None = None)
Register an accessor that extends `rx` with
custom behavior.

Parameters:
**name: str**
The name of the accessor will be attribute-accessible under.

**accessor: Callable\[\[rx\], any\]**
A callable that will return the accessor namespace object given the
`rx` object it is registered on.

**predicate: Callable\[\[Any\], bool\] \| None**

classmethod register_display_handler(obj_type, handler, **kwargs)
Register a display handler for a specific type of object.

Makes it possible to define custom display options for specific objects.

Parameters:
**obj_type: type \| callable**
The type to register a custom display handler on.

**handler: Viewable \| callable**
A Viewable or callable that is given the object to be displayed and the
custom keyword arguments.

**kwargs: dict\[str, Any\]**
Additional display options to register for this type.

classmethod register_method_handler(method, handler)
Register a handler that is called when a specific method on an object is
called.

property rx: reactive_ops
The reactive operations namespace.

Provides reactive versions of operations that cannot be made reactive
through operator overloading. This includes operations such as
`.rx.and_` and
`.rx.bool`.

References

For more details, see the user guide: [https://param.holoviz.org/user_guide/Reactive_Expressions.html#special-methods-on-rx](https://param.holoviz.org/user_guide/Reactive_Expressions.html#special-methods-on-rx)

Examples

Create a reactive expression:

\>\>\>
import
param \>\>\>
rx_expression =
param.rx(1)

Retrieve the current value reactively:

\>\>\> a_value
=
rx_expression.rx.value

Use special methods from the reactive ops namespace for reactive
operations:

\>\>\> condition
=
rx_expression.rx.and\_(True)
\>\>\> piped
=
rx_expression.rx.pipe(lambda
x:
x \*
2)

panel.serve(panels: TViewableFuncOrPath \| dict\[str, TViewableFuncOrPath\], port: int = 0, address: str \| None = None, websocket_origin: str \| list\[str\] \| None = None, loop: IOLoop \| None = None, show: bool = True, start: bool = True, title: str \| None = None, verbose: bool = True, location: bool = True, threaded: bool = False, admin: bool = False, **kwargs) → StoppableThread \| Server
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

class panel.widget(\*, name)
Bases: `ParameterizedFunction`

Attempts to find a widget appropriate for a given value.

Parameters:
**label: str**
The label of the resulting widget.

**value: Any**
The value to deduce a widget from.

**default: Any**
The default value for the resulting widget.

****params: Any**
Additional keyword arguments to pass to the widget.

Methods

|  |  |
|----|----|
| [widget_from_iterable](#panel.widget.widget_from_iterable)(o, label) | Make widgets from an iterable. |
| [widget_from_single_value](#panel.widget.widget_from_single_value)(o, label) | Make widgets from single values, which can be used as parameter defaults. |
| [widget_from_tuple](#panel.widget.widget_from_tuple)(o, label, default) | Make widgets from a tuple abbreviation. |

Returns:
Widget

**Parameter Definitions**

------------------------------------------------------------------------

static widget_from_iterable(o, label: str) → Widget \| None
Make widgets from an iterable. This should not be done for a string or
tuple.

static widget_from_single_value(o, label: str) → Widget \| None
Make widgets from single values, which can be used as parameter
defaults.

static widget_from_tuple(o, label: str, default) → Widget \| None
Make widgets from a tuple abbreviation.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
