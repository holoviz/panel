# Tutorial Outline

These guides already exists

- [development](development.md)
- [interactivity](interactivity.md)
- [layouts](layouts.md)
- [param](param.md)
- [styling](styling.md)

They should be refactored into the below

## Basic

These guides are for you that is just starting to discover Panel.

You will learn to develop and deploy basic tools and apps that can be contained within a single Python file or notebook.

WIDGET and `.bind` BASED APPROACH

- [ ] Getting installed (just a link to getting started)
  - [ ] Using a pre-installed environment for this tutorial: Purpose is to lower Barrier of entry. Make it possible to do at large conference with poor internet. Use Binder, Github spaces, Anaconda Notebooks ???
- [ ] [Serve Apps](https://github.com/holoviz/panel/blob/docs_fixes_1.4_a1_review/doc/tutorials/beginner/serve.md)
- [ ] [Build a Chat Bot](https://github.com/holoviz/panel/blob/docs_fixes_1.4_a1_review/doc/tutorials/beginner/build_chatbot.md)
- [ ] [Develop in a notebook](https://github.com/holoviz/panel/blob/docs_fixes_1.4_a1_review/doc/tutorials/beginner/develop_notebook.md)
- [ ] [Develop in an editor](https://github.com/holoviz/panel/blob/docs_fixes_1.4_a1_review/doc/tutorials/beginner/develop_editor.md)
- [ ] [Display objects with `pn.panel`](https://github.com/holoviz/panel/blob/docs_fixes_1.4_a1_review/doc/tutorials/beginner/pn_panel.md)
- [ ] [Display objects with Panes](https://github.com/holoviz/panel/blob/docs_fixes_1.4_a1_review/doc/tutorials/beginner/panes.md)
- [ ] [Layout objects](https://github.com/holoviz/panel/blob/docs_fixes_1.4_a1_review/doc/tutorials/beginner/layouts.md)
- [ ] [Accept User Input](https://github.com/holoviz/panel/blob/docs_fixes_1.4_a1_review/doc/tutorials/beginner/widgets.md)
- [ ] Add interactivity easily and efficiently: `pn.bind`. Also with `watch=True`.
- [ ] Size components: sizing_mode, height/ width, max_height/ max_width
- [ ] Align components: `align`, `margin`, Spacer/ HSpacer/ VSpacer
- [ ] Style components with designs
- [ ] Style components with styles
- [ ] Organize and Style with templates
- [ ] Indicate busy-ness with indicators
- [ ] Improve performance: caching
- [ ] Dynamic Layouts: generators
- [ ] Build a static, Financial Report: Save to .html, use .embed, Can be done after "Layout Objects"
- [ ] Build a Todo App: Can be done after "pn.bind"
- [ ] Build a Wind Turbine Dashboard: Puts everything together
- [ ] Build a Stock Prices Streaming Application: Puts everything together
- [ ] Share your work: Deploy to Hugging Face Spaces

## Intermediate

These guides are for you that is ready to navigate and explore more advanced features of Panel.

You will learn to develop and deploy complex tools and multi-page apps to support advanced use cases.

CLASS BASED APPROACH. UNDERSTANDING OF PARAM AND SUPPLEMENTARY APIs

- [ ] [Serve Apps](https://github.com/holoviz/panel/blob/docs_fixes_1.4_a1_review/doc/tutorials/intermediate/serve.md)
- [ ] [Develop in an editor](https://github.com/holoviz/panel/blob/docs_fixes_1.4_a1_review/doc/tutorials/intermediate/develop_editor.md)
- [ ] [Structure with a DataStore](https://github.com/holoviz/panel/blob/docs_fixes_1.4_a1_review/doc/tutorials/intermediate/structure_data_store.md)
- [ ] Work with Parameters and Events: Param
- [ ] Organize Components flexibly with FlexBox
- [ ] Schedule Tasks: pn.state.onload, pn.state.schedule_task, pn.state.add_periodic_callback, pn.state.on_session_created, pn.state.on_session_destroyed, async generators, pn.state.execute
- [ ] [Structuring Applications](https://holoviz-dev.github.io/panel/tutorials/structure.html) (I think this is a great tutorial !!!): Class based approach
- [ ] Build custom components easily: Viewable
- [ ] Sync location
- [ ] Add interactivity flexibly: `.rx`
- [ ] Add side effects: `.watch` (or `watch=True` ?)
- [ ] Avoid Common Mistakes: Defining "global" widgets in utility modules that ends up being shared between users.
- [ ] Show progress dynamically with generators
- [ ] [Enable Throtttling](../how_to/performance/throttling.html)
- [ ] Share your work: Embed, Save, link to other deployment options including WASM
- [ ] Build maintainable apps: Class based approach, `@pn.depends`
- [ ] Organizing your code: How to organize the code into sections or modules for efficient maintenance and reuse (data, models, plots, components, app).
- [ ] Improve performance by using async and threads
- [ ] Testing

## Extending 

These guides are for you that is ready to pioneer and push the boundaries of what can be achieved with Panel.

You will learn how to extend Panel to support your domain or specialized use cases.

- [ ] Develop and share custom components: ReactiveHTML/ ReactiveESM
- [ ] Develop and share custom Bokeh models
- [ ] Add custom Authentication
- [ ] Javascript
- [ ] Customizing Panel. For example for your brand.
