import importlib.util
import subprocess
import sys

import pytest


@pytest.mark.skipif(not importlib.util.find_spec("cryptography"), reason='cryptography is not installed')
def test_oauth_secret_command():
    cmd = [sys.executable, "-m", "panel", "oauth-secret"]
    p = subprocess.Popen(cmd, shell=False, text=True, stdout=subprocess.PIPE)
    p.wait()

    try:
        assert len(p.stdout.read()) == 45
    finally:
        p.stdout.close()
