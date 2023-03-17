import json
import os
import sys

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


def clean_js_version(version):
    version = version.replace('-', '')
    for dev in ('a', 'b', 'rc'):
        version = version.replace(dev+'.', dev)
    return version

class PanelBuildHook(BuildHookInterface):

    PLUGIN_NAME = "bundle"

    def validate_version(self):
        from panel import __version__ as version
        if 'post' in version:
            return
        with open('./panel/package.json') as f:
            package_json = json.load(f)
        js_version = package_json['version']
        version = version.split('+')[0]
        if any(dev in version for dev in ('a', 'b', 'rc')) and not '-' in js_version:
            raise ValueError(f"panel.js dev versions ({js_version}) must "
                             "must separate dev suffix with a dash, e.g. "
                             "v1.0.0rc1 should be v1.0.0-rc.1.")
        if version != 'None' and version != clean_js_version(js_version) and not '.dev' in version:
            raise ValueError(f"panel.js version ({js_version}) does not match "
                             f"panel version ({version}). Cannot build release.")

    def initialize(self, version, build_data):
        from bokeh.ext import build

        from panel.compiler import bundle_resources

        self.validate_version()

        if 'PANEL_LITE' in os.environ:
            print("Skipping bundling steps for LITE build")
            return

        print("Bundling custom model resources:")
        bundle_resources()

        print("Building custom models:")
        panel_dir = os.path.join(os.path.dirname(__file__), "panel")
        build(panel_dir)
        if sys.platform != "win32":
            # npm can cause non-blocking stdout; so reset it just in case
            import fcntl
            flags = fcntl.fcntl(sys.stdout, fcntl.F_GETFL)
            fcntl.fcntl(sys.stdout, fcntl.F_SETFL, flags&~os.O_NONBLOCK)
