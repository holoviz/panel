if (window.ace != null) {
  window._define_requirejs = window.define
  window._require_requirejs = window.require
  function custom_define (e, t, i) {
	if (e.startsWith != null && e.startsWith("ace")) {
      window._define_ace(e, t, i);
	} else {
      window._define_requirejs(e, t, i);
	}
  }
  function custom_require (e, t, i, r) {
	if (e.length && e[0].startsWith("ace")) {
      window._require_ace(e, t, i, r);
	} else {
      window._require_requirejs(e, t, i, r);
	}
  }
  window.define = custom_define
  window.require = custom_require
}
