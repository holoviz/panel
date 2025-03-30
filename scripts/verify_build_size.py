import sys

from pathlib import Path

EXPECTED_SIZES_MB = {
    "conda": 25,
    "npm": 25,
    "sdist": 30,
    "whl": 30,
}

GLOB_PATH = {
    "conda": "dist/*.tar.bz2",
    "npm": "panel/*.tgz",
    "sdist": "dist/*.tar.gz",
    "whl": "dist/*.whl",
}

PATH = Path(__file__).parents[1]


def main(build):
    files = list(PATH.rglob(GLOB_PATH[build]))
    assert len(files) == 1, f"Expected one {build} file, got {len(files)}"

    size = files[0].stat().st_size / 1024**2
    assert size < EXPECTED_SIZES_MB[build], f"{build} file is too large: {size:.2f} MB"
    print(f"{build} file size: {size:.2f} MB")


if __name__ == "__main__":
    main(sys.argv[1])
