const pyodideWorker = new Worker(DOCUMENTATION_OPTIONS.URL_ROOT + '_static/PyodideWebWorker.js');

pyodideWorker.documents = {}
pyodideWorker.busy = false
pyodideWorker.queues = new Map()

function uid() {
  return String(
    Date.now().toString(32) +
      Math.random().toString(16)
  ).replace(/\./g, '')
}

function send_change(jsdoc, doc_id, event) {
  if (event.setter_id == 'py') {
    return
  } else if (pyodideWorker.busy && event.model && event.attr) {
    let events = []
    if (pyodideWorker.queues.has(doc_id)) {
      for (const old_event of pyodideWorker.queues.get(doc_id)) {
        if (!(old_event.model === event.model && old_event.attr === event.attr)) {
          events.push(old_event)
        }
      }
    }
    events.push(event)
    pyodideWorker.queues.set(doc_id, events)
    return
  }
  const patch = jsdoc.create_json_patch([event])
  const uuid = uid()
  pyodideWorker.busy = uuid
  pyodideWorker.postMessage({type: 'patch', patch: patch, id: doc_id, uuid})
}

pyodideWorker.onmessage = async (event) => {
  const button = document.getElementById(`button-${event.data.id}`)
  const output = document.getElementById(`output-${event.data.id}`)
  const stdout = document.getElementById(`stdout-${event.data.id}`)
  const stderr = document.getElementById(`stderr-${event.data.id}`)
  const msg = event.data;

  if (msg.uuid == pyodideWorker.busy) {
    if (pyodideWorker.queues.size) {
      const [msg_id, events] = pyodideWorker.queues.entries().next().value
      const patch = pyodideWorker.documents[msg_id].create_json_patch(events)
      const uuid = uid()
      pyodideWorker.busy = uuid
      pyodideWorker.postMessage({type: 'patch', patch: patch, id: msg_id, uuid})
      pyodideWorker.queues.delete(msg_id)
    } else {
      pyodideWorker.busy = false
    }
  }

  if (msg.type === 'loading') {
    _ChangeTooltip(button, msg.msg)
    _ChangeIcon(button, iconLoading)
  } else if (msg.type === 'loaded') {
    _ChangeTooltip(button, 'Executing code')
  } else if (msg.type === 'error') {
    _ChangeTooltip(button, msg.msg)
    _ChangeIcon(button, iconError)
  } else if (msg.type === 'idle') {
    _ChangeTooltip(button, 'Executed successfully')
    _ChangeIcon(button, iconLoaded)
  } else if (msg.type === 'stdout') {
    const stdout = document.getElementById(`stdout-${msg.id}`)
    stdout.style.display = 'block';
    stdout.innerHTML += msg.content
  } else if (msg.type === 'stderr') {
    const stderr = document.getElementById(`stderr-${msg.id}`)
    stderr.style.display = 'block';
    stderr.innerHTML += msg.content
  } else if (msg.type === 'render') {
    output.style.display = 'block';
    output.setAttribute('class', 'pyodide-output live')
    if (msg.mime === 'application/bokeh') {
      const [view] = await Bokeh.embed.embed_item(JSON.parse(msg.content))

      // Setup bi-directional syncing
      pyodideWorker.documents[msg.id] = jsdoc = view.model.document
      jsdoc.on_change(send_change.bind(null, jsdoc, msg.id), false)
    } else if (msg.mime === 'text/plain') {
      output.innerHTML = `<pre>${msg.content}</pre>`;
    } else if (msg.mime === 'text/html') {
      output.innerHTML = `<div class="pyodide-output-wrapper">${msg.content}</div>`
    }
    pyodideWorker.postMessage({type: 'rendered', id: msg.id, mime: msg.mime})
  } else if (msg.type === 'patch') {
    pyodideWorker.documents[msg.id].apply_json_patch(msg.patch, msg.buffers, setter_id='py')
  }
};

window.pyodideWorker = pyodideWorker;