import hashlib
import json
import os.path

from glob import glob

from packaging.utils import parse_wheel_filename


def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()

    with open(file_path, "rb") as file:
        for byte_block in iter(lambda: file.read(4096), b""):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()


with open("package-lock.json") as f:
    package = json.load(f)
pyodide_version = package["packages"]["node_modules/pyodide"]["version"]

path = "pyodide-lock.json"
url = f"https://cdn.jsdelivr.net/pyodide/v{pyodide_version}/full"

with open(path) as f:
    data = json.load(f)

# micropip.freeze points bundled packages at the local node_modules cache
for p in data["packages"].values():
    if not p["file_name"].startswith("http"):
        p["file_name"] = f'{url}/{os.path.basename(p["file_name"])}'

# pyodide.loadPackage does not terminate on the panel / panel-material-ui cycle
for dep in data["packages"]["panel"]["depends"]:
    depends = data["packages"].get(dep, {}).get("depends", [])
    if "panel" in depends:
        depends.remove("panel")


whl_files = glob("../../dist/*.whl")
for whl_file in whl_files:
    name, version, *_ = parse_wheel_filename(os.path.basename(whl_file))

    package = data["packages"][name]
    package["version"] = str(version)
    package["file_name"] = os.path.basename(whl_file)
    package["sha256"] = calculate_sha256(whl_file)
    package["imports"] = [name]


with open(path, "w") as f:
    data = json.dump(data, f)
