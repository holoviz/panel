"""Script to sync tags from upstream repository to forked repository."""

import sys

from subprocess import run


def main(package: str) -> None:
    origin = run(
        ["git", "remote", "get-url", "origin"], check=True, capture_output=True
    )
    upstream = run(
        ["git", "remote", "get-url", "upstream"], check=False, capture_output=True
    )
    url = (
        f"https://github.com/holoviz/{package}.git"
        if origin.stdout.startswith(b"http")
        else f"git@github.com:holoviz/{package}.git"
    )

    if url == origin.stdout.strip().decode():
        print("Not a forked repository, exiting.")
        return
    elif upstream.returncode:
        print(f"Adding {url!r} as remote upstream")
        run(["git", "remote", "add", "upstream", url], check=True, capture_output=True)

    print(f"Syncing tags from {package} repository with your forked repository")
    run(["git", "fetch", "--tags", "upstream"], check=True, capture_output=True)
    run(["git", "push", "--tags"], check=True, capture_output=True)


if __name__ == "__main__":
    main(sys.argv[1])
