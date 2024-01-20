# Tutorial Outline

These guides already exists

- [components](components.md)
- [development](development.md)
- [interactivity](interactivity.md)
- [layouts](layouts.md)
- [param](param.md)
- [structure](structure.md)
- [styling](styling.md)

They should be refactored into the below

## Beginner: Core. Most important, basic stuff to learn, Can be done at 3 hour training event?

- [ ] Getting installed (just a link to getting started)
  - [ ] Using a pre-installed environment for this tutorial: Purpose is to lower Barrier of entry. Make it possible to do at large conference with poor internet. Use Binder, Github spaces, Anaconda Notebooks ???

- [ ] Serve your first apps: panel serve, --autoreload --show, --help, multiple files: [Working Document](https://github.com/holoviz/panel/blob/docs_fixes_1.4_a1_review/doc/tutorials/panel_serve.md)
- [ ] Develop App in an editor (pn.extension, .servable(), panel serve, autoreload, show, multi page app, inspecting objects, getting help, link to: pn.serve) [Working Document](https://github.com/holoviz/panel/blob/docs_fixes_1.4_a1_review/doc/tutorials/develop_editor.md)
- [ ] Develop App in a notebook (pn.extension, .servable(), panel preview, panel serve, autoreload, multipage app, inspecting objects, getting help, links to how-to guides for more advanced topics like inspecting browser console and hard refreshing the browser, maybe link to colab Panel notebook). [Working Document](https://github.com/holoviz/panel/blob/docs_fixes_1.4_a1_review/doc/tutorials/develop_notebook.md)
- [ ] Display Content Easily: pn.panel - Panels print function [Working Document](https://github.com/holoviz/panel/blob/docs_fixes_1.4_a1_review/doc/tutorials/display_pn_panel.md)
- [ ] Display Content Efficiently:  panes - Panels output components
- [ ] Organize Components Easily: Columns and Rows, sizing_mode. links to Layouts in Components Gallery
- [ ] Work with Parameters and Events: Param
- [ ] Accept User Input: widgets. Panels input components
- [ ] Add interactivity easily and efficiently: `pn.bind`
- [ ] Add interactivity flexibly: `.rx`
- [ ] Style components with designs
- [ ] Style components with styles
- [ ] Organize and Style apps with templates
- [ ] Indicate busy-ness with indicators
- [ ] Show progress dynamically with generators
- [ ] Improve performance: caching
- [ ] Deploy an app: Hugging Face Spaces

## Intermediate: Less important, basic stuff to learn

- [ ] Organize Components Part II: margin, align
- [ ] Organize Components flexibly with FlexBox
- [ ] Schedule Tasks: pn.state.onload, pn.state.schedule_task, pn.state.add_periodic_callback, pn.state.on_session_created, pn.state.on_session_destroyed, async generators, pn.state.execute
- [ ] [Structuring Applications](https://holoviz-dev.github.io/panel/tutorials/structure.html) (I think this is a great tutorial !!!): Class based approach
- [ ] Avoid Common Mistakes: Defining "global" widgets in utility modules that ends up being shared between users.
- [ ] Customizing Panel. For example for your brand.
- [ ] Use panels documentation in your browser: Panelite

## Advanced: Things our users might find scary to learn and that is not needed at first

- [ ] Scheduling tasks: on_load, globally
- [ ] Improve performance by using async and threads
- [ ] Build reusable components easily: Viewable
- [ ] Build reusable components with power: ReactiveESM
- [ ] Build maintainable apps: Class based approach
- [ ] Build testable Apps: pytest
- [ ] Organize your projects: How to organize the code into sections or modules for efficient maintenance and reuse (data, models, plots, components, app).

## Reference Examples

These could be maintained blog posts. Maybe its the App Gallery. Maybe its the HoloViz Examples. To be determined.

- [ ] Build a Todo App
- [ ] Build a Dashboard
  - [ ] With Matplotlib
  - [ ] With hvPlot and HoloViews
  - [ ] With Plotly
  - [ ] Interactive Table
- [ ] Build a Streaming Dashboard
- [ ] Build a ChatInterface
