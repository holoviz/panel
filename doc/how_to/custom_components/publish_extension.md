# Publish a Panel Extension

If you've built a custom Panel component—a `Viewer`, `JSComponent`, `ReactComponent`, or `ReactiveHTML` subclass—and want to share it as a reusable, installable Python package, the **Panel Extension Copier Template** gives you a fully configured project scaffold to do just that.

## What the template provides

The [`copier-template-panel-extension`](https://github.com/panel-extensions/copier-template-panel-extension) generates a project pre-configured with:

- **pytest** for testing
- **MkDocs + mkdocstrings** for auto-generated API documentation hosted on GitHub Pages
- **GitHub Actions** CI/CD for automated testing and publishing
- **Pixi** for reproducible environment management

## Quickstart

Make sure you have [Pixi](https://pixi.sh) installed, then run:

```bash
pixi exec --spec copier --spec ruamel.yaml -- \
  copier copy --trust \
  https://github.com/panel-extensions/copier-template-panel-extension \
  panel-name-of-extension
```

You'll be prompted for a few details such as extension type, project slug, and author info.

From there, follow the template's [step-by-step guide](https://github.com/panel-extensions/copier-template-panel-extension#getting-started) to set up GitHub Pages, link your package to PyPI, and publish your first release by creating a git tag.

## Example extensions

The [**panel-extensions**](https://github.com/orgs/panel-extensions/repositories) GitHub organisation hosts extensions built with this template. Browse it to see real-world examples and find components you can use directly:

| Extension | Description |
|-----------|-------------|
| [panel-material-ui](https://github.com/panel-extensions/panel-material-ui) | Material UI components for Panel |
| [panel-graphic-walker](https://github.com/panel-extensions/panel-graphic-walker) | Graphic Walker drag-and-drop data explorer |
| [panel-splitjs](https://github.com/panel-extensions/panel-splitjs) | Responsive draggable split-panel layout |
| [panel-reactflow](https://github.com/panel-extensions/panel-reactflow) | Reactflow node-graph wrapper |
| [panel-web-llm](https://github.com/panel-extensions/panel-web-llm) | Client-side in-browser LLM interface |
| [panel-full-calendar](https://github.com/panel-extensions/panel-full-calendar) | FullCalendar integration |
| [panel-precision-slider](https://github.com/panel-extensions/panel-precision-slider) | Slider with fine-tuned precision control and direct text input |
| [panel-live-server](https://github.com/panel-extensions/panel-live-server) | Live server for displaying Panel outputs to humans and AI agents |
