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

See the [Component Gallery](https://panel.holoviz.org/reference/index.html#extensions) for community extensions built on Panel's custom component APIs.
