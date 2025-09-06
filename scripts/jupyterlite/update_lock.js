const { loadPyodide } = require("pyodide");
const fs = require("fs");

async function main() {
  const extra = fs.readFileSync("extra_packages.json", "utf8");

  let pyodide = await loadPyodide();
  await pyodide.loadPackage(["micropip"]);

  output = await pyodide.runPythonAsync(`
import json
import micropip
extra = json.loads("""${extra}""")
await micropip.install(extra)
micropip.freeze()
`);
  fs.writeFileSync("pyodide-lock.json", output);
}

main();
