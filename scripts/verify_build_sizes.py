# /// script
# dependencies = ["requests"]
# ///
import os
import sys

import requests

PACKAGE = "panel"


EXPECTED_SIZES_MB = {
    "npm": 25,
    "pip": 60,  # sdist + wheel
    "cdn": 30,
    "conda": 25,
}

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
    "X-GitHub-Api-Version": "2022-11-28",
}


def main(run_number: int):
    url = f"https://api.github.com/repos/holoviz/{PACKAGE}/actions/workflows/build.yaml/runs"
    resp = requests.get(url, headers=HEADERS, timeout=20)
    assert resp.ok

    for run in resp.json()["workflow_runs"]:
        if run["run_number"] == run_number:
            break

    assert run["run_number"] == run_number, "Run number not found!"

    artifact_url = run["url"] + "/artifacts"
    artifact_resp = requests.get(artifact_url, headers=HEADERS, timeout=20)
    assert artifact_resp.ok

    sizes = {v["name"]: v["size_in_bytes"] for v in artifact_resp.json()["artifacts"]}

    print(sizes)
    for k, v in EXPECTED_SIZES_MB.items():
        assert sizes[k] < v * 1024**2, f"{k} artifact ({sizes[k] / 1024**2:0.2f} MB) larger than {v} MB."


if __name__ == "__main__":
    main(int(sys.argv[1]))
