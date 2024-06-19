import json
import sys

from pathlib import Path
from subprocess import (
    PIPE, STDOUT, CalledProcessError, run,
)

from packaging.version import InvalidVersion, Version

PACKAGE = "panel"

PACKAGE_JSON = Path(f"{PACKAGE}/package.json")
PACKAGE_LOCK_JSON = Path(f"{PACKAGE}/package-lock.json")
GREEN, RED, RESET = "\033[92m", "\033[91m", "\033[0m"


def git(*args):
    return run(["git", *args], check=True, stdout=PIPE, stderr=STDOUT).stdout.strip().decode()


def js_update(version):
    print(f"{GREEN}[{PACKAGE}]{RESET} Updating package.json")
    js_ver = version.removeprefix("v")
    for n in ["a", "b", "c"]:
        js_ver = js_ver.replace(n, f"-{n}.")

    package_json = json.loads(PACKAGE_JSON.read_text())
    package_json["version"] = js_ver
    PACKAGE_JSON.write_text(f"{json.dumps(package_json, indent=2)}\n")
    print(f"{GREEN}[{PACKAGE}]{RESET} Updating package-lock.json")
    try:
        run(["npm", "update", PACKAGE], cwd=PACKAGE, stderr=PIPE, stdout=PIPE, check=True)
    except CalledProcessError as e:
        print(f"{RED}[{PACKAGE}]{RESET} Failed to update package-lock.json: {e}")
        sys.exit(1)

    git("add", f"{PACKAGE}/package.json", f"{PACKAGE}/package-lock.json")
    git("commit", "-m", f"Update package.json to {js_ver}", "--no-verify")


def validate_version(version):
    try:
        version = f"v{Version(version)}"
    except InvalidVersion:
        print(f"{RED}[{PACKAGE}]{RESET} Invalid version: {version}")
        sys.exit(1)
    try:
        git("rev-parse", "HEAD", version)  # Will fail if it does not exits
        print(f"{RED}[{PACKAGE}]{RESET} Tag {version} already exists")
        sys.exit(1)
    except CalledProcessError:
        pass
    return version


def main(version):
    version = validate_version(version)
    js_update(version)

    commit = git("rev-parse", "HEAD")
    git("tag", version, commit, "-m", version.replace("v", "Version "))
    print(f"{GREEN}[{PACKAGE}]{RESET} Tagged {version}")


if __name__ == "__main__":
    assert len(sys.argv) == 2, "Usage: pixi bump-version <version>"
    main(*sys.argv[1:])
