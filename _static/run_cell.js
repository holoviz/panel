/**
 * SVG files for our copy buttons
 */
let iconRun = `
<svg class="pyodide-run-icon" style="width:32px;height:25px" viewBox="0 0 24 24">
    <path stroke="none" fill="#28a745" d="M8,5.14V19.14L19,12.14L8,5.14Z" />
</svg>`

let iconLoading = `
<svg class="pyodide-loading-icon" style="width:32px;height:25px" viewBox="0 0 24 24">
    <path fill="currentColor" d="M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.21,8.95 2.27,9.22 2.46,9.37L4.57,11C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.21,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.94C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.67 16.04,18.34 16.56,17.94L19.05,18.95C19.27,19.03 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z" />
</svg>`

let iconLoaded = `<svg class="pyodide-loaded-icon" style="width:32px;height:25px" viewBox="0 0 24 24">
    <path fill="#28a745" d="M9,20.42L2.79,14.21L5.62,11.38L9,14.77L18.88,4.88L21.71,7.71L9,20.42Z" />
</svg>`

let iconError = `<svg class="pyodide-error-icon" style="width:32px;height:25px" viewBox="0 0 24 24">
    <path fill="#ff0000" d="M12,2C17.53,2 22,6.47 22,12C22,17.53 17.53,22 12,22C6.47,22 2,17.53 2,12C2,6.47 6.47,2 12,2M15.59,7L12,10.59L8.41,7L7,8.41L10.59,12L7,15.59L8.41,17L12,13.41L15.59,17L17,15.59L13.41,12L17,8.41L15.59,7Z" />
</svg>`

let iconAlert = `<svg class="pyodide-alert-icon" style="width:32px;height:25px" viewBox="0 0 24 24">
    <path fill="#f6be00" d="M13 13H11V7H13M11 15H13V17H11M15.73 3H8.27L3 8.27V15.73L8.27 21H15.73L21 15.73V8.27L15.73 3Z" />
</svg>`

/**
 * Set up run for code blocks
 */

const _runWhenDOMLoaded = cb => {
  if (document.readyState != 'loading') {
    cb()
  } else if (document.addEventListener) {
    document.addEventListener('DOMContentLoaded', cb)
  } else {
    document.attachEvent('onreadystatechange', function() {
      if (document.readyState == 'complete') cb()
    })
  }
}

const _codeCellId = index => `codecell${index}-py`

// Changes tooltip text for two seconds, then changes it back
const _ChangeTooltip = (el, newText) => {
  const oldText = el.getAttribute('data-tooltip')
  el.setAttribute('data-tooltip', newText)
}

// Changes the copy button icon for two seconds, then changes it back
const _ChangeIcon = (el, icon) => {
  el.innerHTML = icon;
}

function executeCell(id) {
  const cell = document.getElementById(id)
  let output = document.getElementById(`output-${id}`)
  let stdout = document.getElementById(`stdout-${id}`)
  let stderr = document.getElementById(`stderr-${id}`)
  if (stdout == null) {
    stdout = document.createElement('pre');
    stdout.setAttribute('id', `stdout-${id}`)
    stdout.setAttribute('class', 'pyodide-stdout')
    cell.parentElement.parentElement.appendChild(stdout)
  }
  if (stderr == null) {
    stderr = document.createElement('pre');
    stderr.setAttribute('id', `stderr-${id}`)
    stderr.setAttribute('class', 'pyodide-stderr')
    cell.parentElement.parentElement.appendChild(stderr)
  }
  if (output == null) {
    output = document.createElement('div');
    output.setAttribute('id', `output-${id}`)
    output.setAttribute('class', 'pyodide-output')
    cell.parentElement.parentElement.appendChild(output)
  }
  window.pyodideWorker.postMessage({
    type: 'execute',
    id: id,
    path: document.location.pathname,
    code: cell.textContent
  })
  cell.setAttribute('executed', true)
}

const _query_params = new Proxy(new URLSearchParams(window.location.search), {
  get: (searchParams, prop) => searchParams.get(prop),
});

let ACCEPTED = false;
let INITIALIZED = 0;
let EXECUTED = false;

const _addRunButtonToCodeCells = () => {
  // If Pyodide Worker hasn't loaded, wait a bit and try again.
  if (window.pyodideWorker === undefined) {
    setTimeout(addRunButtonToCodeCells, 250)
    return
  }

  // Add copybuttons to all of our code cells
  const RUNBUTTON_SELECTOR = 'div.pyodide div.highlight pre';
  const codeCells = document.querySelectorAll(RUNBUTTON_SELECTOR)

  INITIALIZED += 1
  codeCells.forEach((codeCell, index) => {
    const id = _codeCellId(index)
    const copybtn = codeCell.parentElement.getElementsByClassName('copybtn')
    if (copybtn.length) {
      copybtn[0].setAttribute('data-clipboard-target', `#${id}`)
    }
    codeCell.setAttribute('id', id)
    codeCell.setAttribute('executed', false)

    // importShim will cause DOMLoaded event to trigger twice so we skip
    // adding buttons the first time
    if ((INITIALIZED < 2) && window.importShim) {
      return
    }

    const RunButton = id =>
    `<button id="button-${id}" class="runbtn o-tooltip--left" data-tooltip="Run cell" data-clipboard-target="#${id}">
      ${iconRun}
    </button>`
    codeCell.insertAdjacentHTML('afterend', RunButton(id))
    const run_button = document.getElementById(`button-${id}`)
    run_button.addEventListener('click', (e) => {
      if (!ACCEPTED) {
        _ChangeTooltip(e.currentTarget, 'Executing this cell will download a Python runtime (typically 40+ MB). Click again to proceed.')
        _ChangeIcon(e.currentTarget, iconAlert)
        ACCEPTED = true
        return
      } else if (!EXECUTED) {
        Bokeh.index.roots.map((v) => v.remove())
        EXECUTED = true
      }
      let i = 0;
      while (true) {
        let cell_id = _codeCellId(i)
        let cell = document.getElementById(cell_id)
        if (cell == null) {
          break
        }
        const output = document.getElementById(`output-${cell_id}`)
        const stdout = document.getElementById(`stdout-${cell_id}`)
        const stderr = document.getElementById(`stderr-${cell_id}`)
        if (cell.getAttribute('executed') == 'false' || i == index) {
          if (output) {
            output.innerHTML = '';
            output.style.display = 'none';
          }
          if (stdout) {
            stdout.innerHTML = '';
            stdout.style.display = 'none';
          }
          if (stderr) {
            stderr.innerHTML = '';
            stderr.style.display = 'none';
          }
          executeCell(cell_id)
        }
        i++;
      }
    })
  })
  if (_query_params.autorun) {
    const id = _codeCellId(0)
    const run_button = document.getElementById(`button-${id}`)
    run_button.click()
    run_button.click()
  }
}

_runWhenDOMLoaded(_addRunButtonToCodeCells)
