importScripts("{{ PYODIDE_URL }}");

function sendPatch(patch, buffers) {
  self.postMessage({
    type: 'patch',
    patch: patch,
    buffers: buffers,
  })
}

async function startApplication() {
  console.log("Loading pyodide!");
  self.pyodide = await loadPyodide();
  self.pyodide.globals.set("sendPatch", sendPatch);
  console.log("Loaded!");
  await self.pyodide.loadPackage("micropip");
  await self.pyodide.runPythonAsync(`
    import micropip
    await micropip.install([{{ env_spec }}]);
  `);
  console.log("Packages loaded!");
  const code = `
  {{ code }}
  `
  const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(code)
  self.postMessage({
    type: 'render',
    docs_json: docs_json,
    render_items: render_items,
    root_ids: root_ids
  });
}

self.onmessage = async (event) => {
  if (event.data.type === 'rendered') {
    self.pyodide.runPythonAsync(`
    import pyodide

    from bokeh.protocol.messages.patch_doc import process_document_events
    from panel.state import state

    def pysync(event):
        json_patch, buffers = process_document_events([event], use_buffers=True)
        buffer_map = {}
        for (ref, buffer) in buffers:
            buffer_map[ref['id']] = pyodide.to_js(buffer).buffer
        sendPatch(json_patch, pyodide.to_js(buffer_map))

    state.curdoc.on_change(pysync)
    state.curdoc.callbacks.trigger_json_event(
        {'event_name': 'document_ready', 'event_values': {}
    })
    `)
  } else if (event.data.type === 'patch') {
    self.pyodide.runPythonAsync(`
    import json
    state.curdoc.apply_json_patch(json.loads('${event.data.patch}'))
    `)
  }
}

startApplication()
