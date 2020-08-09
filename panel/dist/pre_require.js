if (window.ace != null) {
  ace.config.set('basePath', 'https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.12/')
  window._require_ace = window.require
  window._define_ace = window.define
  delete window.require
  delete window.define
}
