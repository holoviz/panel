import subprocess
import sys


def test_oauth_secret_command():
    cmd = [sys.executable, "-m", "panel", "oauth-secret"]
    p = subprocess.Popen(cmd, shell=False, text=True, stdout=subprocess.PIPE)
    p.wait()

    try:
        assert len(p.stdout.read()) == 45
    finally:
        p.stdout.close()
