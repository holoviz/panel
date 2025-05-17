import "https://cdn.jsdelivr.net/npm/@finos/perspective-viewer/dist/cdn/perspective-viewer.js"
import "https://cdn.jsdelivr.net/npm/@finos/perspective-viewer-datagrid/dist/cdn/perspective-viewer-datagrid.js"
import "https://cdn.jsdelivr.net/npm/@finos/perspective-viewer-d3fc/dist/cdn/perspective-viewer-d3fc.js"
import perspective from "https://cdn.jsdelivr.net/npm/@finos/perspective/dist/cdn/perspective.js";

async function render({ model, el }) {
    const elem = document.createElement('perspective-viewer');
    elem.style.height = '100%';
    elem.style.width = '100%';
    el.appendChild(elem);

    const websocket = await perspective.websocket(
        model.get("websocket")
    );
    const server_table = await websocket.open_table(model.get("value"));
    await elem.load(server_table);
}
export default { render };
