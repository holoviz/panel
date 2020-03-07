import panel as pn
import param
pn.config.sizing_mode="stretch_width"

pn.config.js_files["webdatarocks-toolbar"]="https://cdn.webdatarocks.com/latest/webdatarocks.toolbar.min.js"
pn.config.js_files["webdatarocks"]="https://cdn.webdatarocks.com/latest/webdatarocks.js"
pn.config.css_files.append("https://cdn.webdatarocks.com/latest/webdatarocks.min.css")


html = """
<div id="wdr-component"></div>
<script>
var pivot = new WebDataRocks({
    container: "#wdr-component",
    toolbar: true,
    report: {
        dataSource: {
            filename: "https://cdn.webdatarocks.com/data/data.csv"
        }
    }
});
</script>"""

class WebDataRocks(pn.pane.WebComponent):
    html = param.String(html)
    properties_to_watch = param.Dict({"toolbar": "toolbar"})

    datasource_filename = param.String()
    toolbar = param.Boolean()

WebDataRocks().servable()