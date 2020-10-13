"""
Utilities for building custom models included in panel.
"""
from __future__ import absolute_import, division, unicode_literals

#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------

def require_components():
    """
    Returns JS snippet to load the required dependencies in the classic
    notebook using REQUIRE JS.
    """
    from .config import config

    configs, requirements, exports = [], [], []
    js_requires = []

    from bokeh.model import Model
    for qual_name, model in Model.model_class_reverse_map.items():
        # We need to enable Models from Panel as well as Panel extensions
        # like awesome_panel_extensions.
        # The Bokeh models do not have "." in the qual_name
        if "." in qual_name:
            js_requires.append(model)

    for export, js in config.js_files.items():
        name = js.split('/')[-1].replace('.min', '').split('.')[-2]
        conf = {'paths': {name: js[:-3]}, 'exports': {name: export}}
        js_requires.append(conf)

    skip_import = {}
    for model in js_requires:
        if hasattr(model, '__js_skip__'):
            skip_import.update(model.__js_skip__)

        if not (hasattr(model, '__js_require__') or isinstance(model, dict)):
            continue

        if isinstance(model, dict):
            model_require = model
        else:
            model_require = model.__js_require__

        model_exports = model_require.pop('exports', {})
        if not any(model_require == config for config in configs):
            configs.append(model_require)

        for req in list(model_require.get('paths', [])):
            if isinstance(req, tuple):
                model_require['paths'][req[0]] = model_require['paths'].pop(req)

            export = req[0] if isinstance(req, tuple) else req
            if export not in model_exports:
                continue

            if isinstance(req, tuple):
                for r in req[1]:
                    if r not in requirements:
                        requirements.append(r)
                req = req[0]
            elif req not in requirements:
                requirements.append(req)

            export = model_exports[req]
            for e in (export if isinstance(export, list) else [export]):
                if export not in exports and export is not None:
                    exports.append(export)
    return configs, requirements, exports, skip_import
