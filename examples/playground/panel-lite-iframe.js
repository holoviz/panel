const welcome=`\
import panel as pn
pn.extension()

pn.pane.Markdown("Welcome! Try clicking the \`run\` button.").servable()
`

const htmlTemplate=`
<!DOCTYPE html>
<html>
<head>
	<title>My Page</title>
    <script src="https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js"></script>
    <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-3.3.0.min.js"></script>
    <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-gl-3.3.0.min.js"></script>
    <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-3.3.0.min.js"></script>
    <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-tables-3.3.0.min.js"></script>
    <script type="text/javascript" src="https://cdn.holoviz.org/panel/1.3.1/dist/panel.min.js"></script>
</head>
<body>
    <div>I am a new template</div>
	<div id="main"></div>
    <div id="loading-spinner" style="height:100px;width:100px">Loading...</div>
</body>
</html>
`

// Fix Panel when running inside an iframe srcdoc
// See https://github.com/holoviz/panel/issues/5506#issuecomment-1784433401
const fixPanel = `
from panel.io.location import Location
Location.param.pathname.regex=r"^$|[\/]|srcdoc$"
print("Panel Location issue fixed")
`

// See https://github.com/holoviz/panel/blob/8579e5cf322604e61b95bb1e10dcc57466298df1/panel/io/convert.py#L87
const pyoidideScript = `
<script type="text/javascript">
async function main() {
    let envSpec =  [{{ env_spec }}]
    envSpec = envSpec.filter(item => !window.envSpec.includes(item));
    if (envSpec.length > 0) {
        console.log("installing: ", envSpec)
        await window.micropip.install(envSpec)
    }
    window.envSpec = window.envSpec.concat(envSpec);


    code = \`{{ code }}\`
    await window.pyodide.runPythonAsync(code);

    window.addEventListener('message', handleMessage);
  }
  main();
<\/script>
`


async function useCustomPyodideScript(){
    command = `
from panel.io import convert
convert.PYODIDE_SCRIPT = \"\"\"
${pyoidideScript}
\"\"\"
print("Changed the PYODIDE_SCRIPT for Panelite")
`
    await window.pyodide.runPythonAsync(command)
}

async function loadPyodideAndPackages(jsglobals){
    _pyodide = await loadPyodide({
        packages: "micropip",
        jsglobals: jsglobals
    })
    window.micropip = _pyodide.pyimport("micropip");
    window.envSpec=[
        'https://cdn.holoviz.org/panel/wheels/bokeh-3.3.0-py3-none-any.whl',
        'https://cdn.holoviz.org/panel/1.3.1/dist/wheels/panel-1.3.1-py3-none-any.whl',
        'pyodide-http==0.2.1'
    ]
    await window.micropip.install(window.envSpec)
    // Todo: https://github.com/holoviz/panel/issues/5811
    window.envSpec = window.envSpec.concat(["panel", "bokeh", "datetime", "random"])
    return _pyodide
}

async function convertToHTML(code){
    await useCustomPyodideScript()

    let command = `

from io import StringIO
from panel.io import convert
from panel.io.convert import script_to_html
from panel.io.resources import set_resource_mode
from bokeh.settings import settings as bk_settings

code = \"\"\"
${fixPanel}

${code}
\"\"\"

def _get_html(code):
    file = StringIO(code)

    try:
        bk_settings.simple_ids.set_value(True)
        with set_resource_mode('cdn'):
            html, _ = script_to_html(file, prerender=False)
    except Exception as ex:
        html = f"Exception: {ex}"
        print(ex)
    finally:
        bk_settings.simple_ids.set_value(False)


    return html.replace("v0.23.4", "v0.24.1")

_get_html(code)
`
    return await window.pyodide.runPythonAsync(command)
}

async function installIfMissing(code, package){
    if (code.includes(package) && !window.envSpec.includes(package)){
        console.log(`installing ${package}`)
        await window.micropip.install(package)
        window.envSpec = window.envSpec.concat([package])
    }
}

async function runCode(code){
    // Todo: panel.io.convert.find_requirements does not find these?
    await installIfMissing(code, 'plotly')
    await installIfMissing(code, 'matplotlib')

    code = `
print('started python')

${code}

print('finished python')`
    html = await convertToHTML(code)
    if (html.startsWith("Exception:")){
        code = `
import panel as pn
pn.extension()
pn.panel("""
${html}
""").servable()
        `
        html = await convertToHTML(code)
    }
    document.open()
    document.write(html)
    document.close()
}
async function handleMessage(event){
    console.log('Received message:');

    await runCode(event.data)
}

window.handleMessage = handleMessage
