"""
Uploads a stripped Pyodide wheel to cdn.holoviz.org for every Bokeh
release on PyPI that is missing there.

``panel convert`` points converted apps at the CDN wheel matching the
Bokeh version installed locally, but a Panel release only uploads the
wheel of the Bokeh version it was built against, so Bokeh releases
between two Panel releases would otherwise never be uploaded.
"""

import argparse
import json
import pathlib
import subprocess
import sys
import tempfile
import urllib.request

from bokeh_wheel import strip_bokeh_wheel
from packaging.version import Version

BUCKET_PATH = "s3://cdn.holoviz.org/panel/wheels/"
# Every release from here on is hosted, older ones were never uploaded
MIN_VERSION = "3.2.2"


def pypi_releases(min_version: Version) -> list[Version]:
    with urllib.request.urlopen("https://pypi.org/pypi/bokeh/json", timeout=60) as response:
        releases = json.load(response)["releases"]
    versions = []
    for version, files in releases.items():
        parsed = Version(version)
        if parsed.is_prerelease or parsed < min_version:
            continue
        if any(f["filename"].endswith("-py3-none-any.whl") and not f["yanked"] for f in files):
            versions.append(parsed)
    return sorted(versions)


def cdn_wheels() -> set[str]:
    listing = subprocess.run(
        ["aws", "s3", "ls", BUCKET_PATH], check=True, capture_output=True, text=True
    ).stdout
    return {line.split()[-1] for line in listing.splitlines() if line.strip()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-version", default=MIN_VERSION, help="Oldest Bokeh release to sync")
    parser.add_argument("--dry-run", action="store_true", help="Only report the missing wheels")
    args = parser.parse_args()

    hosted = cdn_wheels()
    missing = [
        version for version in pypi_releases(Version(args.min_version))
        if f"bokeh-{version}-py3-none-any.whl" not in hosted
    ]
    if not missing:
        print("All Bokeh wheels are on the CDN.")
        return
    print("Missing Bokeh wheels:", ", ".join(map(str, missing)))
    if args.dry_run:
        return

    with tempfile.TemporaryDirectory() as tmp:
        download_dir, out_dir = pathlib.Path(tmp, "download"), pathlib.Path(tmp, "out")
        out_dir.mkdir()
        for version in missing:
            subprocess.run(
                [
                    sys.executable, "-m", "pip", "download", f"bokeh=={version}",
                    "--no-deps", "--only-binary=:all:", "--ignore-requires-python",
                    "-d", str(download_dir),
                ],
                check=True,
            )
            wheel = download_dir / f"bokeh-{version}-py3-none-any.whl"
            stripped = strip_bokeh_wheel(wheel, out_dir)
            subprocess.run(["aws", "s3", "cp", str(stripped), BUCKET_PATH], check=True)


if __name__ == "__main__":
    main()
