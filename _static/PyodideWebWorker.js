importScripts("https://cdn.jsdelivr.net/pyodide/v0.28.2/full/pyodide.js");

const QUEUE = [];

const REQUIRES = {"gallery/altair_brushing": ["altair"], "gallery/gapminders": ["altair", "plotly", "hvplot", "matplotlib"], "gallery/glaciers": ["holoviews", "colorcet", "hvplot"], "gallery/hvplot_explorer": ["hvplot", "scipy"], "gallery/iris_kmeans": ["hvplot", "scikit-learn", "bokeh_sampledata"], "gallery/nyc_deckgl": ["fastparquet", "pyodide-http"], "gallery/penguin_crossfilter": ["hvplot"], "gallery/penguin_kmeans": ["altair"], "gallery/portfolio_optimizer": ["hvplot", "scipy"], "gallery/streaming_videostream": ["pillow", "scikit-image"], "gallery/VTKInteractive": ["pyvista"], "gallery/VTKSlicer": ["holoviews", "scipy"], "gallery/windturbines": ["hvplot", "fastparquet"], "gallery/xgboost_classifier": ["pandas", "scikit-learn", "xgboost"], "getting_started/build_app": ["hvplot", "matplotlib"], "how_to/apis/callbacks": ["hvplot"], "how_to/apis/interact": ["hvplot"], "how_to/apis/parameterized": ["hvplot"], "how_to/apis/reactive": ["hvplot"], "how_to/apis/examples/stocks_hvplot": ["hvplot"], "how_to/apis/examples/stocks_plotly": ["plotly"], "how_to/custom_components/examples/plot_viewer": ["hvplot"], "how_to/interactivity/hvplot_interactive": ["hvplot"], "how_to/io/download_simple": ["XlsxWriter", "fastparquet"], "how_to/layout/examples/dynamic_tabs": ["altair", "vega-datasets", "hvplot", "matplotlib", "plotly"], "how_to/links/examples/holoviews_glyph_link": ["holoviews"], "how_to/links/examples/plotly_link": ["plotly"], "how_to/param/examples/loading": ["holoviews"], "how_to/pipeline/complex_pipeline": ["holoviews"], "how_to/pipeline/control_flow": ["holoviews"], "how_to/pipeline/pipeline_layout": ["holoviews"], "how_to/pipeline/simple_pipeline": ["holoviews"], "reference/layouts/GridSpec": ["holoviews"], "reference/layouts/GridStack": ["holoviews"], "reference/layouts/Swipe": ["hvplot", "scipy"], "reference/panes/Audio": ["scipy"], "reference/panes/DataFrame": ["streamz", "bokeh_sampledata"], "reference/panes/DeckGL": ["pydeck"], "reference/panes/ECharts": ["pyecharts"], "reference/panes/Folium": ["folium"], "reference/panes/HoloViews": ["hvplot", "matplotlib", "plotly", "scipy"], "reference/panes/IPyWidget": ["ipywidgets", "ipyvolume", "ipyleaflet", "ipywidgets_bokeh"], "reference/panes/Matplotlib": ["matplotlib", "ipywidgets", "ipympl", "ipywidgets_bokeh"], "reference/panes/Param": ["hvplot"], "reference/panes/Plotly": ["plotly"], "reference/panes/Reacton": ["reacton", "pandas", "jupyter_bokeh"], "reference/panes/Streamz": ["streamz", "altair", "pandas"], "reference/panes/Vega": ["altair", "vega_datasets"], "reference/panes/VTK": ["vtk", "pyvista"], "reference/panes/VTKJS": ["pyodide-http"], "reference/panes/VTKVolume": ["pyvista"], "reference/templates/Bootstrap": ["holoviews"], "reference/templates/FastGridTemplate": ["holoviews"], "reference/templates/FastListTemplate": ["holoviews"], "reference/templates/GoldenLayout": ["holoviews"], "reference/templates/Material": ["holoviews"], "reference/templates/React": ["holoviews"], "reference/templates/Vanilla": ["holoviews"], "reference/widgets/DataFrame": ["bokeh_sampledata"], "reference/widgets/Tabulator": ["bokeh_sampledata"], "reference/widgets/FileDownload": ["bokeh_sampledata"]}

function sendPatch(patch, buffers, cell_id) {
  self.postMessage({
    type: 'patch',
    patch: patch,
    buffers: buffers,
    id: cell_id
  })
}

function sendStdout(cell_id, stdout) {
  self.postMessage({
    type: 'stdout',
    content: stdout,
    id: cell_id
  })
}
function sendStderr(cell_id, stderr) {
  self.postMessage({
    type: 'stderr',
    content: stderr,
    id: cell_id
  })
}

async function loadApplication(cell_id, path) {
  console.log("Loading pyodide!");
  self.pyodide = await loadPyodide();
  self.pyodide.globals.set("sendPatch", sendPatch);
  self.pyodide.globals.set("sendStdout", sendStdout);
  self.pyodide.globals.set("sendStderr", sendStderr);
  console.log("Loaded!");
  await self.pyodide.loadPackage("micropip");
  const packages = ['https://cdn.holoviz.org/panel/wheels/bokeh-3.8.2-py3-none-any.whl', 'https://cdn.holoviz.org/panel/wheels/panel-1.8.7-py3-none-any.whl', 'pyodide-http'];
  if (path != null) {
    for (const key of Object.keys(REQUIRES)) {
      if (path.replace('.html', '').endsWith(key.replace('.md', ''))) {
        for (const req of REQUIRES[key]) {
          packages.push(req)
        }
      }
    }
  }

  await self.pyodide.runPythonAsync("")
  self.pyodide.runPython("import micropip")
  for (const pkg of packages) {
    self.postMessage({
      type: 'loading',
      msg: `Loading ${pkg}`,
      id: cell_id
    });
    await self.pyodide.runPythonAsync(`
      await micropip.install('${pkg}', keep_going=True, reinstall=True);
    `);
  }
  console.log("Packages loaded!");
}

const autodetect_deps_code = `
import json
try:
    from panel.io.mime_render import find_requirements
except Exception:
    from panel.io.mime_render import find_imports as find_requirements
json.dumps(find_requirements(msg.to_py()['code']))`

const exec_code = `
from functools import partial
from panel.io.pyodide import pyrender
from js import console

msg = msg.to_py()
code = msg['code']
stdout_cb = partial(sendStdout, msg['id'])
stderr_cb = partial(sendStderr, msg['id'])
target = f"output-{msg['id']}"
pyrender(code, stdout_cb, stderr_cb, target)`

const onload_code = `
msg = msg.to_py()
if msg['mime'] == 'application/bokeh':
    from panel.io.pyodide import _link_docs_worker
    from panel.io.state import state
    doc = state.cache[f"output-{msg['id']}"]
    _link_docs_worker(doc, sendPatch, msg['id'], 'js')`

const patch_code = `
from panel import state

try:
    from pane.io.pyodide import _convert_json_patch
    patch = _convert_json_patch(msg.patch)
except:
    patch = msg.patch.to_py()
doc = state.cache[f"output-{msg.id}"]
doc.apply_json_patch(patch, setter='js')`

const MESSAGES = {
  patch: patch_code,
  execute: exec_code,
  rendered: onload_code
}

self.onmessage = async (event) => {
  let resolveExecution, rejectExecution;
   const executing = new Promise(function(resolve, reject){
    resolveExecution = resolve;
    rejectExecution = reject;
  });

  const prev_msg = QUEUE[0]
  const msg = {...event.data, executing}
  QUEUE.unshift(msg)

  if (prev_msg) {
    self.postMessage({
      type: 'loading',
      msg: 'Awaiting previous cells',
      id: msg.id
    });
    await prev_msg.executing
  }

  // Init pyodide
  if (self.pyodide == null) {
    self.postMessage({
      type: 'loading',
      msg: 'Loading pyodide',
      id: msg.id
    });
    await loadApplication(msg.id, msg.path)
    self.postMessage({
      type: 'loaded',
      id: msg.id
    });
  }

  // Handle message
  if (!MESSAGES.hasOwnProperty(msg.type)) {
    console.warn(`Service worker received unknown message type '${msg.type}'.`)
    resolveExecution()
    self.postMessage({
      type: 'idle',
      id: msg.id
    });
    return
  }

  if (msg.type === 'execute') {
    let deps
    try {
      self.pyodide.globals.set('msg', msg)
      deps = self.pyodide.runPython(autodetect_deps_code)
    } catch(e) {
      deps = '[]'
      console.warn(`Auto-detection of dependencies failed with error: ${e}`)
    }
    for (const pkg of JSON.parse(deps)) {
      self.postMessage({
        type: 'loading',
        msg: `Loading ${pkg}`,
        id: msg.id
      });
      try {
        await self.pyodide.runPythonAsync(`await micropip.install('${pkg}', keep_going=True)`)
      } catch(e) {
        console.log(`Auto-detected dependency ${pkg} could not be installed.`)
      }
    }
  }

  try {
    self.pyodide.globals.set('msg', msg)
    let out = await self.pyodide.runPythonAsync(MESSAGES[msg.type])
    resolveExecution()
    if (out == null) {
      out = new Map()
    }
    if (out.has('content')) {
      self.postMessage({
        type: 'render',
        id: msg.id,
        content: out.get('content'),
        mime: out.get('mime_type')
      });
    }
    if (out.has('stdout') && out.get('stdout').length) {
      self.postMessage({
        type: 'stdout',
        content: out.get('stdout'),
        id: msg.id
      });
    }
    if (out.has('stderr') && out.get('stderr').length) {
      self.postMessage({
        type: 'stderr',
        content: out.get('stderr'),
        id: msg.id
      });
    }
    self.postMessage({
      type: 'idle',
      id: msg.id,
      uuid: msg.uuid
    });
  } catch (e) {
    const traceback = `${e}`
    const tblines = traceback.split('\n')
    self.postMessage({
      type: 'error',
      traceback: traceback,
      msg: tblines[tblines.length-2],
      id: msg.id
    });
    resolveExecution()
    throw(e)
  }
}