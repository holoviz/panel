const pyodideWorker = new Worker("./{{ name }}.js");
pyodideWorker.busy = false
pyodideWorker.queue = []

function send_change(jsdoc, event) {
  if (event.setter_id != null && event.setter_id == 'py') {
    return
  } else if (pyodideWorker.busy && event.model && event.attr) {
    let events = []
    for (const old_event of pyodideWorker.queue) {
      if (!(old_event.model === event.model && old_event.attr === event.attr)) {
        events.push(old_event)
      }
    }
    events.push(event)
    pyodideWorker.queue = events
    return
  }
  const patch = jsdoc.create_json_patch([event])
  pyodideWorker.busy = true
  pyodideWorker.postMessage({type: 'patch', patch: patch})
}

pyodideWorker.onmessage = async (event) => {
  const msg = event.data

  const body = document.getElementsByTagName('body')[0]
  const loading_msgs = document.getElementsByClassName('pn-loading-msg')
  if (msg.type === 'idle') {
    if (pyodideWorker.queue.length) {
      const patch = pyodideWorker.jsdoc.create_json_patch(pyodideWorker.queue)
      pyodideWorker.busy = true
      pyodideWorker.queue = []
      pyodideWorker.postMessage({type: 'patch', patch: patch})
    } else {
      pyodideWorker.busy = false
    }
  } else if (msg.type === 'status') {
    let loading_msg
    if (loading_msgs.length) {
      loading_msg = loading_msgs[0]
    } else if (body.classList.contains('pn-loading')) {
      loading_msg = document.createElement('div')
      loading_msg.classList.add('pn-loading-msg')
      body.appendChild(loading_msg)
    }
    if (loading_msg != null) {
      loading_msg.innerHTML = msg.msg
    }
  } else if (msg.type === 'render') {
    const docs_json = JSON.parse(msg.docs_json)
    const render_items = JSON.parse(msg.render_items)
    const root_ids = JSON.parse(msg.root_ids)

    // Remap roots in message to element IDs
    const root_els = document.querySelectorAll('[data-root-id]')
    const data_roots = []
    for (const el of root_els) {
       el.innerHTML = ''
       data_roots.push([el.getAttribute('data-root-id'), el.id])
    }
    data_roots.sort((a, b) => a[0]<b[0] ? -1: 1)
    const roots = {}
    for (let i=0; i<data_roots.length; i++) {
      roots[root_ids[i]] = data_roots[i][1]
    }
    render_items[0]['roots'] = roots
    render_items[0]['root_ids'] = root_ids

    // Embed content
    const [views] = await Bokeh.embed.embed_items(docs_json, render_items)

    // Remove loading spinner and message
    body.classList.remove("pn-loading", "{{ loading_spinner }}")
    for (const loading_msg of loading_msgs) {
      loading_msg.remove()
    }

    // Setup bi-directional syncing
    pyodideWorker.jsdoc = jsdoc = [...views.roots.values()][0].model.document
    jsdoc.on_change(send_change.bind(null, jsdoc), false)
    pyodideWorker.postMessage({'type': 'rendered'})
    pyodideWorker.postMessage({'type': 'location', location: JSON.stringify(window.location)})
  } else if (msg.type === 'patch') {
    pyodideWorker.jsdoc.apply_json_patch(msg.patch, msg.buffers, setter_id='py')
  }
};
