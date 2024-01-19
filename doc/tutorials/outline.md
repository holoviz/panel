# Tutorial Outline

## Beginner: Most important, basic stuff to learn

- [ ] Getting installed (just a link to getting started)
  - [ ] Use a cloud development environment: Binder or Github spaces
  - [ ] Use panels documentation in your browser: Panelite
- [x] Serve your first apps: panel serve, --autoreload --show, --help, multiple files,
- [x] Develop App in an editor (pn.extension, .servable(), panel serve, autoreload, show, multi page app, inspecting objects, getting help, link to: pn.serve)
- [x] Develop App in a notebook (pn.extension, .servable(), panel preview, panel serve, autoreload, multipage app, inspecting objects, getting help, links to how-to guides for more advanced topics like inspecting browser console and hard refreshing the browser, maybe link to colab Panel notebook).
- [x] Display Content Easily: pn.panel - Panels print function
- [ ] Display Content Efficiently:  panes - Panels output components
- [ ] Organize Components Easily: Columns, Rows, sizing_mode. links to Layouts in Components Gallery
- [ ] Organize Components Flexibly: FlexBox
- [ ] Work with Parameters and Events: Param
- [ ] Accept User Input: widgets. Panels input components
- [ ] Add interactivity easily and efficiently: `pn.bind`
- [ ] Add interactivity flexibly: `.rx`
- [ ] Style components with designs
- [ ] Organize and Style apps with templates
- [ ] Indicate busy-ness with indicators
- [ ] Show progress dynamically with generators
- [ ] Improve performance: caching
- [ ] Deploy an app: Hugging Face Spaces

## Intermediate: Less important, basic stuff to learn

- [ ] [Structuring Applications](https://holoviz-dev.github.io/panel/tutorials/structure.html) (I think this is a great tutorial !!!): Class based approach
- [ ] Life Cycle Hooks: pn.state.onload etc. [Better header should be found]

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
