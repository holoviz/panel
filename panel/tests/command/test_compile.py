import pathlib
import subprocess
import sys

from panel.custom import JSComponent

CWD = pathlib.Path(__file__).parent


class JSTestComponent(JSComponent):

    _esm = "export function render() { console.log('foo') }"


class JSTestComponentWithShared(JSComponent):

    _esm = "import {log} from './utils'\n\nexport function render() { log('foo') }"
    _esm_shared = {
        'utils': "export function log(msg) { console.log(msg) }"
    }

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


def test_compile_component_with_shared_file(py_file):
    cmd = [sys.executable, "-m", "panel", "compile", "panel.tests.command.test_compile:JSTestComponentWithShared", "--unminified"]
    p = subprocess.Popen(cmd, shell=False, cwd=CWD)
    p.wait()

    bundle = CWD / "JSTestComponentWithShared.bundle.js"
    try:
        assert bundle.is_file()
        assert 'function log(msg) {\n  console.log(msg);\n}' in bundle.read_text()
        assert 'function render() {\n  log("foo");\n}' in bundle.read_text()
    finally:
        bundle.unlink()
        p.kill()
