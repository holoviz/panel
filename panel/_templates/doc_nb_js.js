(function(root) {
  function embed_document(root) {
    var docs_json = {{ docs_json }};
    var render_items = {{ render_items }};
    root.Bokeh.embed.embed_items_notebook(docs_json, render_items);
  }
  if (root.Bokeh !== undefined && root.Bokeh.Panel !== undefined{% for req in requirements %} && root['{{ req }}'] !== undefined {% endfor %}{% if ipywidget %}&& (root.Bokeh.Models.registered_names().indexOf("ipywidgets_bokeh.widget.IPyWidget") > -1){% endif %}) {
    embed_document(root);
  } else {
    var attempts = 0;
    var timer = setInterval(function(root) {
      if (root.Bokeh !== undefined && root.Bokeh.Panel !== undefined{% for req in requirements %} && root['{{ req }}'] !== undefined{% endfor %}{% if ipywidget %}&& (root.Bokeh.Models.registered_names().indexOf("ipywidgets_bokeh.widget.IPyWidget") > -1){% endif %}) {
        clearInterval(timer);
        embed_document(root);
      } else if (document.readyState == "complete") {
        attempts++;
        if (attempts > 100) {
          clearInterval(timer);
          console.log("Bokeh: ERROR: Unable to run BokehJS code because BokehJS library is missing");
        }
      }
    }, 10, root)
  }
})(window);
