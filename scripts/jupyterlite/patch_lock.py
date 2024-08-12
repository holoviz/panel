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


with open("package.json") as f:
    package = json.load(f)
pyodide_version = package["dependencies"]["pyodide"].removeprefix("^")

path = "pyodide-lock.json"
url = f"https://cdn.jsdelivr.net/pyodide/v{pyodide_version}/full"

with open(path) as f:
    data = json.load(f)

for p in data["packages"].values():
    if not p["file_name"].startswith("http"):
        p["file_name"] = os.path.join(url, p["file_name"])


# Special handling of holonote
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
