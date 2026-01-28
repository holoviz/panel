importScripts("https://cdn.jsdelivr.net/pyodide/v0.28.2/full/pyodide.js");

function sendPatch(patch, buffers, msg_id) {
  self.postMessage({
    type: 'patch',
    patch: patch,
    buffers: buffers
  })
}

async function startApplication() {
  console.log("Loading pyodide...");
  self.postMessage({type: 'status', msg: 'Loading pyodide'})
  self.pyodide = await loadPyodide();
  self.pyodide.globals.set("sendPatch", sendPatch);
  console.log("Loaded pyodide!");
  const data_archives = [];
  for (const archive of data_archives) {
    let zipResponse = await fetch(archive);
    let zipBinary = await zipResponse.arrayBuffer();
    self.postMessage({type: 'status', msg: `Unpacking ${archive}`})
    self.pyodide.unpackArchive(zipBinary, "zip");
  }
  await self.pyodide.loadPackage("micropip");
  self.postMessage({type: 'status', msg: `Installing environment`})
  try {
    await self.pyodide.runPythonAsync(`
      import micropip
      await micropip.install(['https://cdn.holoviz.org/panel/wheels/bokeh-3.8.2-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.8.7/dist/wheels/panel-1.8.7-py3-none-any.whl', 'pyodide-http', 'param']);
    `);
  } catch(e) {
    console.log(e)
    self.postMessage({
      type: 'status',
      msg: `Error while installing packages`
    });
  }
  console.log("Environment loaded!");
  self.postMessage({type: 'status', msg: 'Executing code'})
  try {
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nfrom panel import state as _pn__state\nfrom panel.io.handlers import CELL_DISPLAY as _CELL__DISPLAY, display, get_figure as _get__figure\n\nimport asyncio\nimport panel as pn\nimport param\n\nfrom panel.custom import JSComponent, ESMEvent\n\n_pn__state._cell_outputs['04c6078a-0398-425c-82f7-d516b01b713d'].append((pn.extension('mathjax', template='material')))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['04c6078a-0398-425c-82f7-d516b01b713d'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['04c6078a-0398-425c-82f7-d516b01b713d'].append(_fig__out)\n\n_pn__state._cell_outputs['9aea88fd-3ae9-453f-a66e-b3bdc44c22e3'].append("""This example demonstrates how to wrap an external library (specifically [WebLLM](https://github.com/mlc-ai/web-llm)) as a \`JSComponent\` and interface it with the \`ChatInterface\`.""")\nMODELS = {\n    'SmolLM2 (130MB)': 'SmolLM2-360M-Instruct-q4f16_1-MLC',\n    'TinyLlama-1.1B-Chat (675 MB)': 'TinyLlama-1.1B-Chat-v1.0-q4f16_1-MLC-1k',\n    'Gemma-2b (2GB)': 'gemma-2-2b-it-q4f16_1-MLC',\n    'Llama-3.2-3B-Instruct (2.2GB)': 'Llama-3.2-3B-Instruct-q4f16_1-MLC',\n    'Mistral-7b-Instruct (5GB)': 'Mistral-7B-Instruct-v0.3-q4f16_1-MLC',\n}\n\nclass WebLLM(JSComponent):\n\n    loaded = param.Boolean(default=False, doc="""\n        Whether the model is loaded.""")\n\n    history = param.Integer(default=3)\n\n    status = param.Dict(default={'text': '', 'progress': 0})\n\n    load_model = param.Event()\n\n    model = param.Selector(default='SmolLM2-360M-Instruct-q4f16_1-MLC', objects=MODELS)\n\n    running = param.Boolean(default=False, doc="""\n        Whether the LLM is currently running.""")\n    \n    temperature = param.Number(default=1, bounds=(0, 2), doc="""\n        Temperature of the model completions.""")\n\n    _esm = """\n    import * as webllm from "https://esm.run/@mlc-ai/web-llm";\n\n    const engines = new Map()\n\n    export async function render({ model }) {\n      model.on("msg:custom", async (event) => {\n        if (event.type === 'load') {\n          if (!engines.has(model.model)) {\n            const initProgressCallback = (status) => {\n              model.status = status\n            }\n            const mlc = await webllm.CreateMLCEngine(\n               model.model,\n               {initProgressCallback}\n            )\n            engines.set(model.model, mlc)\n          }\n          model.loaded = true\n        } else if (event.type === 'completion') {\n          const engine = engines.get(model.model)\n          if (engine == null) {\n            model.send_msg({'finish_reason': 'error'})\n          }\n          const chunks = await engine.chat.completions.create({\n            messages: event.messages,\n            temperature: model.temperature ,\n            stream: true,\n          })\n          model.running = true\n          for await (const chunk of chunks) {\n            if (!model.running) {\n              break\n            }\n            model.send_msg(chunk.choices[0])\n          }\n        }\n      })\n    }\n    """\n\n    def __init__(self, **params):\n        super().__init__(**params)\n        if pn.state.location:\n            pn.state.location.sync(self, {'model': 'model'})\n        self._buffer = []\n\n    @param.depends('load_model', watch=True)\n    def _load_model(self):\n        self.loading = True\n        self._send_msg({'type': 'load'})\n\n    @param.depends('loaded', watch=True)\n    def _loaded_model(self):\n        self.loading = False\n\n    @param.depends('model', watch=True)\n    def _update_load_model(self):\n        self.loaded = False\n\n    def _handle_msg(self, msg):\n        if self.running:\n            self._buffer.insert(0, msg)\n\n    async def create_completion(self, msgs):\n        self._send_msg({'type': 'completion', 'messages': msgs})\n        while True:\n            await asyncio.sleep(0.01)\n            if not self._buffer:\n                continue\n            choice = self._buffer.pop()\n            yield choice\n            reason = choice['finish_reason']\n            if reason == 'error':\n                raise RuntimeError('Model not loaded')\n            elif reason:\n                return\n\n    async def callback(self, contents: str, user: str):\n        if not self.loaded:\n            if self.loading:\n                yield pn.pane.Markdown(\n                    f'## \`{self.model}\`\\n\\n' + self.param.status.rx()['text']\n                )\n            else:\n                yield 'Load the model'\n            return\n        self.running = False\n        self._buffer.clear()\n        message = ""\n        async for chunk in self.create_completion([{'role': 'user', 'content': contents}]):\n            message += chunk['delta'].get('content', '')\n            yield message\n\n    def menu(self):\n        status = self.param.status.rx()\n        return pn.Column(\n            pn.widgets.Select.from_param(self.param.model, sizing_mode='stretch_width'),\n            pn.widgets.FloatSlider.from_param(self.param.temperature, sizing_mode='stretch_width'),\n            pn.widgets.Button.from_param(\n                self.param.load_model, sizing_mode='stretch_width',\n                disabled=self.param.loaded.rx().rx.or_(self.param.loading)\n            ),\n            pn.indicators.Progress(\n                value=(status['progress']*100).rx.pipe(int), visible=self.param.loading,\n                sizing_mode='stretch_width'\n            ),\n            pn.pane.Markdown(status['text'], visible=self.param.loading)\n        )\n_pn__state._cell_outputs['a663e937-797b-468f-875d-5bb8c2af002b'].append("""Having implemented the \`WebLLM\` component we can render the WebLLM UI:""")\nllm = WebLLM()\n\nintro = pn.pane.Alert("""\n\`WebLLM\` runs large-language models entirely in your browser.\nWhen visiting the application the first time the model has\nto be downloaded and loaded into memory, which may take \nsome time. Models are ordered by size (and capability),\ne.g. SmolLLM is very quick to download but produces poor\nquality output while Mistral-7b will take a while to\ndownload but produces much higher quality output.\n""".replace('\\n', ' '))\n\n_pn__state._cell_outputs['58269444-868b-41e4-abe2-c4fcf031dc4b'].append((pn.Column(\n    llm.menu(),\n    intro,\n    llm\n).servable(area='sidebar')))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['58269444-868b-41e4-abe2-c4fcf031dc4b'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['58269444-868b-41e4-abe2-c4fcf031dc4b'].append(_fig__out)\n\n_pn__state._cell_outputs['96229aa4-c5ed-4c4e-944a-789ee65d768f'].append("""And connect it to a \`ChatInterface\`:""")\nchat_interface = pn.chat.ChatInterface(callback=llm.callback)\nchat_interface.send(\n    "Load a model and start chatting.",\n    user="System",\n    respond=False,\n)\n\nllm.param.watch(lambda e: chat_interface.send(f'Loaded \`{e.obj.model}\`, start chatting!', user='System', respond=False), 'loaded')\n\n_pn__state._cell_outputs['6f899068-8975-4cf4-9e1d-f3fdb5772a71'].append((pn.Row(chat_interface).servable(title='WebLLM')))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['6f899068-8975-4cf4-9e1d-f3fdb5772a71'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['6f899068-8975-4cf4-9e1d-f3fdb5772a71'].append(_fig__out)\n\n\nawait write_doc()`)
    self.postMessage({
      type: 'render',
      docs_json: docs_json,
      render_items: render_items,
      root_ids: root_ids
    })
  } catch(e) {
    const traceback = `${e}`
    const tblines = traceback.split('\n')
    self.postMessage({
      type: 'status',
      msg: tblines[tblines.length-2]
    });
    throw e
  }
}

self.onmessage = async (event) => {
  const msg = event.data
  if (msg.type === 'rendered') {
    self.pyodide.runPythonAsync(`
    from panel.io.state import state
    from panel.io.pyodide import _link_docs_worker

    _link_docs_worker(state.curdoc, sendPatch, setter='js')
    `)
  } else if (msg.type === 'patch') {
    self.pyodide.globals.set('patch', msg.patch)
    self.pyodide.runPythonAsync(`
    from panel.io.pyodide import _convert_json_patch
    state.curdoc.apply_json_patch(_convert_json_patch(patch), setter='js')
    `)
    self.postMessage({type: 'idle'})
  } else if (msg.type === 'location') {
    self.pyodide.globals.set('location', msg.location)
    self.pyodide.runPythonAsync(`
    import json
    from panel.io.state import state
    from panel.util import edit_readonly
    if state.location:
        loc_data = json.loads(location)
        with edit_readonly(state.location):
            state.location.param.update({
                k: v for k, v in loc_data.items() if k in state.location.param
            })
    `)
  }
}

startApplication()