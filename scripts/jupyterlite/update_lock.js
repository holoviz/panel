const { loadPyodide } = require("pyodide");
const fs = require("fs");

async function main() {
  const wheels = fs.readdirSync("../../dist").filter((file) => file.endsWith(".whl"));

  let pyodide = await loadPyodide();
  await pyodide.loadPackage(["micropip"]);
  pyodide.FS.mkdirTree("/packed_wheels");
  for (const wheel of wheels) {
    pyodide.FS.writeFile(`/packed_wheels/${wheel}`, fs.readFileSync(`../../dist/${wheel}`));
  }
  const extra = wheels.map((file) => `emfs:/packed_wheels/${file}`);

  const output = await pyodide.runPythonAsync(`
import importlib.metadata
import json
import micropip
extra = ${JSON.stringify(extra)}
await micropip.install(extra)
lock = json.loads(micropip.freeze())
for module, distributions in importlib.metadata.packages_distributions().items():
    for distribution in distributions:
        package = lock["packages"].get(distribution.lower().replace("_", "-"))
        if package is not None and package["file_name"].endswith(".whl") and module not in package["imports"]:
            package["imports"].append(module)
json.dumps(lock)
`);
  fs.writeFileSync("pyodide-lock.json", output);
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
