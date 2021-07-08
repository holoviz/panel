(function(root) {
  function embed_document(root) {
    var docs_json = {{ docs_json }};
    var render_items = {{ render_items }};
    root.Bokeh.embed.embed_items_notebook(docs_json, render_items);
  }
  if (root.Bokeh !== undefined && root.Bokeh.Panel !== undefined{% for reqs in requirements %} && ({% for req in reqs %}{% if loop.index0 > 0 %}||{% endif %} root['{{ req }}'] !== undefined{% endfor %}){% endfor %}{% if ipywidget %}&& (root.Bokeh.Models.registered_names().indexOf("ipywidgets_bokeh.widget.IPyWidget") > -1){% endif %}) {
    embed_document(root);
  } else {
    var attempts = 0;
    var timer = setInterval(function(root) {
      if (root.Bokeh !== undefined && root.Bokeh.Panel !== undefined{% for reqs in requirements %} && ({% for req in reqs %}{% if loop.index0 > 0 %} || {% endif %}root['{{ req }}'] !== undefined{% endfor %}){% endfor %}{% if ipywidget %}&& (root.Bokeh.Models.registered_names().indexOf("ipywidgets_bokeh.widget.IPyWidget") > -1){% endif %}) {
        clearInterval(timer);
        embed_document(root);
      } else if (document.readyState == "complete") {
        attempts++;
        if (attempts > 200) {
          clearInterval(timer);
          console.log("Bokeh: ERROR: Unable to run BokehJS code because BokehJS library is missing");
        }
      }
    }, 25, root)
  }
})(window);
