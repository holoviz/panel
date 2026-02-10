# Panel does not work with Pyodide v0.29.x

## Summary

Panel 1.8.7 crashes the browser tab when used with Pyodide v0.29.x. The tab crashes during package installation (micropip.install of bokeh/panel wheels), before any Panel code executes. Panel works correctly with Pyodide v0.28.2.

## Reproduction

Save as `test.html` and serve with `python -m http.server`:

```html
<!DOCTYPE html>
<html>
  <head>
    <script type="text/javascript" src="https://cdn.jsdelivr.net/pyodide/v0.28.2/full/pyodide.js"></script>
    <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-3.8.2.js"></script>
    <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-3.8.2.min.js"></script>
    <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-tables-3.8.2.min.js"></script>
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/@holoviz/panel@1.8.7/dist/panel.min.js"></script>
  </head>
  <body>
    <div id="app"></div>
    <script type="text/javascript">
      async function main() {
        let pyodide = await loadPyodide();
        await pyodide.loadPackage("micropip");
        const micropip = pyodide.pyimport("micropip");
        await micropip.install([
          "https://cdn.holoviz.org/panel/1.8.7/dist/wheels/bokeh-3.8.2-py3-none-any.whl",
          "https://cdn.holoviz.org/panel/1.8.7/dist/wheels/panel-1.8.7-py3-none-any.whl"
        ]);
        pyodide.runPython(`
          import panel as pn
          pn.extension(sizing_mode="stretch_width")
          slider = pn.widgets.FloatSlider(start=0, end=10, name='Amplitude')
          def callback(new):
              return f'Amplitude is: {new}'
          pn.Row(slider, pn.bind(callback, slider)).servable(target='app');
        `);
      }
      main();
    </script>
  </body>
</html>
```

## Expected behavior

The slider app renders and is interactive.

## Actual behavior

The browser tab crashes (Chrome shows "Aw, Snap!" or similar) during package installation. No errors appear in the console because the crash kills the tab before any output.

## What works

Changing the Pyodide version from v0.28.2 to v0.28.2 fixes the crash:

```diff
-<script src="https://cdn.jsdelivr.net/pyodide/v0.28.2/full/pyodide.js"></script>
+<script src="https://cdn.jsdelivr.net/pyodide/v0.28.2/full/pyodide.js"></script>
```

## Possible causes

- **Pyodide v0.29.x upgraded to Python 3.13.2 and Emscripten 4.0.9** with an ABI break. Panel's pre-built wheels may be incompatible with the new ABI.
- **JSPI (JavaScript Promise Integration)** became enabled by default in Chrome 137+ and Pyodide v0.28+ uses it. v0.29.x may have changed JSPI behavior that interacts poorly with Bokeh/Panel's async rendering.
- **WebAssembly exception handling** was changed in v0.29.x (switched to native Wasm exceptions for C++ errors and setjmp/longjmp), which could affect how Pyodide handles errors during wheel installation.

## Impact

- The docs currently pin Pyodide v0.28.2, so the documented examples still work.
- However, PyScript (which bundles its own Pyodide version) may default to v0.29.x in newer releases, breaking PyScript-based Panel apps.
- Users who follow the common pattern of loading the latest Pyodide from CDN (`/pyodide/v0.28.2/full/`) will hit this crash.

## Environment

- Panel 1.8.7
- Bokeh 3.8.2 (JS and wheel)
- Pyodide v0.28.2 (crashes), v0.28.2 (works)
- Chrome on Linux
