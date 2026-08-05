# JupyterLab Support Matrix

Panel supports developing and previewing apps in **JupyterLab 4.4, 4.5, and 4.6**.

---

## Supported versions

| Package | Supported / required |
|---------|----------------------|
| JupyterLab | **4.4.x**, **4.5.x** (including 4.5.9), **4.6.x** (`>=4.4,<5`) |
| `pyviz_comms` | **`>= 3.0.2`** (ships `@pyviz/jupyterlab_pyviz`) |
| Panel | Current mainline with jupyter_server extension entry points |

JupyterLab **3.x** is no longer covered by the default `pyviz_comms` lower bound (3.x targets JupyterLab 4). JupyterLab **5.x** is out of scope until `pyviz_comms` and Panel adapt separately.

## Recommended install

Same environment for JupyterLab and your project:

```bash
pip install "panel[jupyter]"
# or
pip install "panel" "pyviz_comms>=3.0.2" "jupyterlab>=4.4,<5"
```

Optional ipywidgets-compatible rendering (VSCode / some notebook UIs):

```bash
pip install jupyter_bokeh
```

### Split environments

If JupyterLab lives in a different environment than the notebook kernel, install **`pyviz_comms >= 3.0.2` in both** environments. Panel must be available in the kernel environment; the JupyterLab environment needs `pyviz_comms` for the frontend labextension and Panel for the Preview server extension when using Preview.

## Features covered

| Feature | Status |
|---------|--------|
| Notebook rendering + bidirectional sync | Supported |
| [Jupyter Panel Preview](jupyterlabpreview) | Supported |
| [Layout Builder](layout_builder) | Supported (`pyviz_comms >= 3.0.2`) |
| Theme sync (`--jp-*` CSS variables) | Supported |
| Keyboard shortcut suppression in Panel outputs | Supported |
| JupyterLite / Panelite | Best-effort via the lite build path |

## Quick verification

```bash
jupyter lab --version
python -c "import pyviz_comms; print(pyviz_comms.__version__)"
jupyter server extension list | grep -i panel
jupyter labextension list | grep -i pyviz
python scripts/check_jupyterlab_stack.py   # from a Panel source checkout
```

Enable the Preview server extension if needed:

```bash
jupyter server extension enable panel.io.jupyter_server_extension --sys-prefix
```

## Related resources

- [Display output in notebooks](notebook)
- [Preview apps in JupyterLab](jupyterlabpreview)
- [Layout Builder](layout_builder)
- Maintainer docs: [compatibility review](../../jupyterlab_4_compatibility_review.md), [solution plan](../../jupyterlab_4_support_solution.md), [stories & tasks](../../jupyterlab_4_support_stories_and_tasks.md)
