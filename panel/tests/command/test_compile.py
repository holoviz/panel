import pathlib
import subprocess
import sys

from panel.custom import JSComponent

CWD = pathlib.Path(__file__).parent


class JSTestComponent(JSComponent):

    _esm = "export function render() { console.log('foo') }"


def test_compile_component(py_file):
    cmd = [sys.executable, "-m", "panel", "compile", "panel.tests.command.test_compile:JSTestComponent", "--unminified"]
    p = subprocess.Popen(cmd, shell=False, cwd=CWD)
    p.wait()

    bundle = CWD / "JSTestComponent.bundle.js"
    try:
        assert bundle.is_file()
        assert 'function render() {\n  console.log("foo");\n}' in bundle.read_text()
    finally:
        bundle.unlink()
        p.kill()
