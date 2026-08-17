# Webllm

```python
import asyncio
import panel as pn
import panel_material_ui as pmui
import param

from panel.custom import JSComponent, ESMEvent

pn.extension('mathjax')
```

This example demonstrates how to wrap an external library (specifically [WebLLM](https://github.com/mlc-ai/web-llm)) as a `JSComponent` and interface it with the `ChatInterface`.

```python
MODELS = {
    'SmolLM2 (130MB)': 'SmolLM2-360M-Instruct-q4f16_1-MLC',
    'TinyLlama-1.1B-Chat (675 MB)': 'TinyLlama-1.1B-Chat-v1.0-q4f16_1-MLC-1k',
    'Gemma-2b (2GB)': 'gemma-2-2b-it-q4f16_1-MLC',
    'Llama-3.2-3B-Instruct (2.2GB)': 'Llama-3.2-3B-Instruct-q4f16_1-MLC',
    'Mistral-7b-Instruct (5GB)': 'Mistral-7B-Instruct-v0.3-q4f16_1-MLC',
}

class WebLLM(JSComponent):

    loaded = param.Boolean(default=False, doc="""
        Whether the model is loaded.""")

    history = param.Integer(default=3)

    status = param.Dict(default={'text': '', 'progress': 0})

    load_model = param.Event()

    model = param.Selector(default='SmolLM2-360M-Instruct-q4f16_1-MLC', objects=MODELS)

    running = param.Boolean(default=False, doc="""
        Whether the LLM is currently running.""")
    
    temperature = param.Number(default=1, bounds=(0, 2), doc="""
        Temperature of the model completions.""")

    _esm = """
    import * as webllm from "https://esm.run/@mlc-ai/web-llm";

    const engines = new Map()

    export async function render({ model }) {
      model.on("msg:custom", async (event) => {
        if (event.type === 'load') {
          if (!engines.has(model.model)) {
            const initProgressCallback = (status) => {
              model.status = status
            }
            const mlc = await webllm.CreateMLCEngine(
               model.model,
               {initProgressCallback}
            )
            engines.set(model.model, mlc)
          }
          model.loaded = true
        } else if (event.type === 'completion') {
          const engine = engines.get(model.model)
          if (engine == null) {
            model.send_msg({'finish_reason': 'error'})
          }
          const chunks = await engine.chat.completions.create({
            messages: event.messages,
            temperature: model.temperature ,
            stream: true,
          })
          model.running = true
          for await (const chunk of chunks) {
            if (!model.running) {
              break
            }
            model.send_msg(chunk.choices[0])
          }
        }
      })
    }
    """

    def __init__(self, **params):
        super().__init__(**params)
        if pn.state.location:
            pn.state.location.sync(self, {'model': 'model'})
        self._buffer = []

    @param.depends('load_model', watch=True)
    def _load_model(self):
        self.loading = True
        self._send_msg({'type': 'load'})

    @param.depends('loaded', watch=True)
    def _loaded_model(self):
        self.loading = False

    @param.depends('model', watch=True)
    def _update_load_model(self):
        self.loaded = False

    def _handle_msg(self, msg):
        if self.running:
            self._buffer.insert(0, msg)

    async def create_completion(self, msgs):
        self._send_msg({'type': 'completion', 'messages': msgs})
        while True:
            await asyncio.sleep(0.01)
            if not self._buffer:
                continue
            choice = self._buffer.pop()
            yield choice
            reason = choice['finish_reason']
            if reason == 'error':
                raise RuntimeError('Model not loaded')
            elif reason:
                return

    async def callback(self, contents: str, user: str):
        if not self.loaded:
            if self.loading:
                yield pn.pane.Markdown(
                    f'## `{self.model}`\n\n' + self.param.status.rx()['text']
                )
            else:
                yield 'Load the model'
            return
        self.running = False
        self._buffer.clear()
        message = ""
        async for chunk in self.create_completion([{'role': 'user', 'content': contents}]):
            message += chunk['delta'].get('content', '')
            yield message

    def menu(self):
        status = self.param.status.rx()
        return pn.Column(
            pmui.Select.from_param(self.param.model, sizing_mode='stretch_width'),
            pmui.FloatSlider.from_param(self.param.temperature, sizing_mode='stretch_width'),
            pmui.Button.from_param(
                self.param.load_model, sizing_mode='stretch_width',
                disabled=self.param.loaded.rx().rx.or_(self.param.loading)
            ),
            pn.indicators.Progress(
                value=(status['progress']*100).rx.pipe(int), visible=self.param.loading,
                sizing_mode='stretch_width'
            ),
            pn.pane.Markdown(status['text'], visible=self.param.loading)
        )
```

Having implemented the `WebLLM` component we can render the WebLLM UI:

```python
llm = WebLLM()

intro = pn.pane.Alert("""
`WebLLM` runs large-language models entirely in your browser.
When visiting the application the first time the model has
to be downloaded and loaded into memory, which may take 
some time. Models are ordered by size (and capability),
e.g. SmolLLM is very quick to download but produces poor
quality output while Mistral-7b will take a while to
download but produces much higher quality output.
""".replace('\n', ' '))

sidebar = pn.Column(
    llm.menu(),
    intro,
    llm
)

sidebar
```

And connect it to a `ChatInterface`:

```python
chat_interface = pmui.ChatInterface(callback=llm.callback)
chat_interface.send(
    "Load a model and start chatting.",
    user="System",
    respond=False,
    sizing_mode="stretch_both"
)

llm.param.watch(lambda e: chat_interface.send(
    f'Loaded `{e.obj.model}`, start chatting!', user='System', respond=False
), 'loaded')

chat_interface
```

### Served App

```python
if pn.state.served:
    pmui.Page(
        main=[chat_interface],
        sidebar=[sidebar],
        title='WebLLM'
    ).servable()
```
