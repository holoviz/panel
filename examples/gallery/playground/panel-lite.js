const loading_spinner = `
<svg xmlns="http://www.w3.org/2000/svg" style="margin: auto; background: none; display: block; shape-rendering: auto;" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid">
<rect x="15" y="30" width="10" height="40" fill="#424242">
  <animate attributeName="opacity" dur="1s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.5 0 0.5 1;0.5 0 0.5 1" values="1;0.2;1" begin="-0.6"/>
</rect><rect x="35" y="30" width="10" height="40" fill="#424242">
  <animate attributeName="opacity" dur="1s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.5 0 0.5 1;0.5 0 0.5 1" values="1;0.2;1" begin="-0.4"/>
</rect><rect x="55" y="30" width="10" height="40" fill="#424242">
  <animate attributeName="opacity" dur="1s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.5 0 0.5 1;0.5 0 0.5 1" values="1;0.2;1" begin="-0.2"/>
</rect><rect x="75" y="30" width="10" height="40" fill="#424242">
  <animate attributeName="opacity" dur="1s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.5 0 0.5 1;0.5 0 0.5 1" values="1;0.2;1" begin="-1"/>
</rect></svg>`

function createElementFromHTML(htmlString) {
    var div = document.createElement('div');
    div.innerHTML = htmlString.trim();

    // Change this to div.childNodes to support multiple top-level nodes.
    return div.firstChild;
  }

class PanelLite {
    constructor(el, code=""){
        this.running=true
        this.code=code
        this._code_run=""
        this._packages_installed=""
        this.el = el
        this.loading_spinner = createElementFromHTML(loading_spinner)
        this.el.appendChild(this.loading_spinner)
        this.main = document.createElement('div');
        this.main.id="main-" + Math.random().toString(16).slice(2)
    }

    async load(){
        await this.load_pyodide_and_micropip()
        await this.import_base_packages()
        await this.import_auto_packages()
        this.running=false
    }
    async load_pyodide_and_micropip(){
        this.log("Loading pyodide")
        this.pyodide = await loadPyodide();
        this.log("Loading micropip")
        await this.pyodide.loadPackage("micropip");
    }

    async import_base_packages(){
        this.log("Loading default packages")
        await this.pyodide.runPythonAsync(`
        import micropip
        await micropip.install(['https://cdn.holoviz.org/panel/wheels/bokeh-3.3.0-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.3.0/dist/wheels/panel-1.3.0-py3-none-any.whl', 'pyodide-http==0.2.1']);
        `)
    }
    async import_auto_packages(){
        const packages_to_install=this.code.split("pn.extension(")[0]
        if (packages_to_install!=this._packages_installed){
            this._packages_installed=packages_to_install
            this.log("Loading custom packages")
            // todo: handle strings that contain """, ''', `, \n etc.
            let command = `
import micropip
from panel.io.mime_render import find_imports
code = '''
${this.code}
'''
requirements = find_imports(code)
# todo: clean up when this in Panel 1.3.1
packages={"transformers_js": "transformers-js-py"}
requirements = [packages.get(package, package) for package in requirements if not package in ['panel', 'bokeh']]
print("installing: ", requirements)
await micropip.install(requirements);
`
            await this.pyodide.runPythonAsync(command);
        } else {
            this.log("No new custom packages to install")
        }
    }

    log(message){
        console.log(message)
    }
    get running(){
        return this._running
    }
    set running(value){
        return this._running=value
    }

    _runCodePre(){
        const body = document.querySelector('body');
        this.main.innerHTML=""
        body.appendChild(this.main);
    }
    _runCodePost(){
        const checkDiv = setInterval(() => {
            if (this.main.hasChildNodes()) {
                clearInterval(checkDiv);
                this.log("Stop running", this.main.innerText)
                this._stop_running()
                if (this._code_run!=this.code){
                    this.log("Code changed. I will run the code again")
                    this._runCode()
                }
            } else {
                this.log('Waiting. The code has not been executed yet');
            }
            }, 200);
    }
    _start_running(){
        this.running=true
        this._code_run=this.code
        setTimeout(() => {
            if (this.running){
                this.main.style.display="none"
                this.loading_spinner.style.display="block";}
        }, "2000");
    }
    _stop_running(){
        this.loading_spinner.style.display="none"
        this.el.appendChild(this.main);
        this.main.style.display="block"
        this.running=false;
    }
    _handle_error(error){

    }

    async _runCode(){
        this._start_running()

        await this.import_auto_packages()
        this._runCodePre()
        const cleanCode=this.code.replace(".servable()", `.servable(target="${this.main.id}")`)
        this.log("Started running the code")
        await this.pyodide.runPythonAsync(cleanCode).then(()=>{
            this.log("Finished running the code")
            this._runCodePost()
        })
    }
    async update(code=null){
        if (code!=null){
            this.code=code
        }
        if (this.running){
            this.log("The code is already running.")
        } else {
            await this._runCode().catch((error)=>{
                this.log('An error occurred:' + error.toString());
                this.main.innerText=error.toString();
                this._stop_running()
                if (this._code_run!=this.code){
                    this.log("Code changed. I will run the code again")
                    this.update()
                }
            })
        }
    }
}

class PanelLiteEditor {
    constructor(el, code){
        this.el = el
        this.panel_lite = new PanelLite(el=el, code=code)
    }
}
