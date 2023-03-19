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
        raise ValueError(self.config, self.app, self.__dict__)
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

        if 'PANEL_LITE' in os.environ:
            print("Skipping bundling steps for LITE build")
            return

        if version != 'editable':
            self.validate_version()

        print("Building custom models:")
        panel_dir = os.path.join(os.path.dirname(__file__), "panel")
        build(panel_dir)

        if version == 'editable':
            print("Skip bundling in editable mode. Ensure you bundle "
                  "resources manually with `panel bundle --all`.")
            return

        from panel.compiler import bundle_resources
        print("Bundling custom model resources:")
        bundle_resources()
        if sys.platform != "win32":
            # npm can cause non-blocking stdout; so reset it just in case
            import fcntl
            flags = fcntl.fcntl(sys.stdout, fcntl.F_GETFL)
            fcntl.fcntl(sys.stdout, fcntl.F_SETFL, flags&~os.O_NONBLOCK)
