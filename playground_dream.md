## Request

**Make it really easy for users to embed, explore, edit, share and maintain Panel apps using Pyodide.**

## As Is

Todays solutions for embedding, exploring, editing, sharing and maintaining Panel apps are not ideal.

- Apps shared via servers are costly
- Apps shared via pyscript/ pyscript.com requires lots of boilerplate code like like html templates
  - The boilerplate is hard to develop and also to maintain.
  - Only a minimum of non-python code should really be required
- The server based editor in Panel Sharing is slow because it reload Pyodide on every *re-run*.
- The Sphinx plugin supports one panel instance in a page only and no template. You can interact with the app, but not the code.

Many alternative frameworks already have live, pyodide based playgrounds (see below *Market Analysis*).

Use Cases

- Embed Panel apps with templates in markdown and html
- Provide powerful Python Editor with hot reload
- Provide interactive and editable galleries of apps at panel.holoviz.org, hvplot.holoviz.org, panel-chat-examples, awesome-panel and more
- Provide a Panel Pyodide pane which can be used to run costly models like audio, image an video models directly in the browser.

- Inspiration: [livecodes.io](https://livecodes.io) | [github/livecodes](https://github.com/live-codes/livecodes) | [github/../python-wasm](https://github.com/live-codes/livecodes/tree/develop/src/livecodes/languages/python-wasm). They are a MIT licensed code sandbox with a pyodide playground that seems to have hot reload.

## "Market Analysis"

### `stlite`

Streamlit has [stlite](https://github.com/whitphx/stlite) and [stlite sharing](https://edit.share.stlite.net/)

[![image](https://github.com/holoviz/panel/assets/42288570/ef5ef2dc-b608-4ac8-b439-f467b081e8de)](https://edit.share.stlite.net/)

### `gradio-lite`

Gradio has [`gradio-lite`](https://www.gradio.app/guides/gradio-lite)

[![image](https://github.com/holoviz/panel/assets/42288570/cdee7156-7b7c-43f4-bb40-b7e77ee03436)](https://www.gradio.app/guides/gradio-lite)

[![image](https://github.com/holoviz/panel/assets/42288570/2306ca66-a81f-4687-9be8-630ca171e6e0)](https://www.gradio.app/playground)

Compared to pyscript.com and stlite **Gradio has minimized the boilerplate code you have to write and maintain**.

I've heard that one of the motivations of Gradio was to enable scikit-learn to better communicate their algorithms by embedding live Gradio apps for users to interact with.

### Shiny live

[Shiny Live](https://shinylive.io/py/examples/#orbit-simulation)

![image](https://github.com/holoviz/panel/assets/42288570/4a92d828-4b85-4195-8ed4-5e4c21ad0b4e)

Note the nice, interactive Python console. Shiny live provides a nice sharing option via a `base64` url.

The look and feel of Shiny Live is a bit dusty compared to `gradio-lite`. Shiny live runs the app inside an iframe.

It does not require a lot to embed the shiny live editor

![image](https://github.com/holoviz/panel/assets/42288570/7672550e-5950-4afc-b2d5-bd842cda84ef)

You can find the implementation of Shiny Live at [github/shinylive](https://github.com/posit-dev/shinylive).

### Py.Cafe

Py.Cafe is an implementation with sharing and hot reload that works really well. I believe they also use uv to install packages very fast.

[example](https://py.cafe/snippet/panel/v1?#c=H4sIACglimkEA01QsU7EMAz9lZAplUoEDAyVbocVsRGEcsTlIqVOSJz2qtP9O07LcMliv-f3nuyL_I4O5CD9lGImkSxCELaIhIZ_Qg1nAiw-oiKYUrAEByNHW8jIro0s3v0AiQMr9F4X_c6iV0yV1GxDbYIl5uD-FQYdjOIEIcSvDWfnM3WDQcEvA9WMYjTypU2ISyOvd0buUk55i4vak_oWevTo1I1bL3ay63SBPNtjAMW5spcZfqvPMAFS4ZW3XTeC1tRusAHcppVOERuwRucd3M8P-ulZPzIV7BoryQFrCL0cfQB2-vi8_gFsz4b8SAEAAA)

### PyScript

PyScript provides an editor that might be useful in https://docs.pyscript.net/2026.2.1/user-guide/editor/.

## SWOT

### Opportunities

### Playgrounds for HoloViz

Panel, hvPlot, HoloViz, Panel-Chat-Examples, Awesome-Panel all try to make holoviz visualizations and apps accessible. A lot of this is static, what is served on servers is costly, there is limited interactivity, browsing the examples is slow.

All of this can be improved by providing a live playground with examples.

### Playgrounds for all of Python

Because `panel` has `pn.panel` we can also provide playgrounds etc. that work for any Python code. If the code  does not contain `.servable()` then just wrap the last value in `pn.panel(last_value).servable()` behind the scenes and display that.

This would give all of Pythons visual frameworks and Pythonistas a huge opportunity.

### Sharing

### `Pyodide` Pane

Some use cases are better served in the browser due to speed or security considerations.

- Running code provided by users or large language models
- Running heavy models on images, audio and video for example coming from the web cam
- Building small games

You might still want to run it on and interact with a server. For example to read from or write to a database in a secure manner.

Examples are [streamlit-webrtc](https://github.com/whitphx/streamlit-webrtc) and [streamlit-fesion](https://github.com/whitphx/streamlit-fesion)

![streamlit-webrtc](https://github.com/holoviz/panel/assets/42288570/594a11af-26de-4518-b0a2-81e7ea5fede2)

#### PyScript.com

Make it much easier to use **`pyscript.com`** by creating a plugin that behind the scenes will convert the Panel Code and render it as a full html template in an iframe.

The pyscript people says that the next version of pyscript will support *hot reload*. In this way we can leverage an existing infrastructure for developing and sharing python apps.

Some people say you should not build your castle in another mans kingdom. But for pyscript.com I think its ok.

## Key implementation ideas

- Instantiate pyoide once. You can save and reload its state. See [github/livecodes/lang-python-wasm-script.ts](https://github.com/live-codes/livecodes/blob/develop/src/livecodes/languages/python-wasm/lang-python-wasm-script.ts).
- Convert code in pyodide using [`script_to_html`](https://github.com/holoviz/panel/blob/f4a51e120295d065a7000fc91af7841c69d56d00/panel/io/convert.py#L174) and (re-render) inside iframe.

## Design - COMING UP

![image](https://github.com/holoviz/panel/assets/42288570/842ac088-816a-4f5c-8b8a-7679a4cdb076)

https://www.online-python.com/#google_vignette

![image](https://github.com/holoviz/panel/assets/42288570/0fd1f568-7c38-495b-bf4b-620426d3d506)
