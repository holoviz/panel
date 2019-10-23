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
        if qual_name.split(".")[0] == "panel":
            js_requires.append(model)

    for export, js in config.js_files.items():
        name = js.split('/')[-1].replace('.min', '').split('.')[-2]
        conf = {'paths': {name: js[:-3]}, 'exports': {name: export}}
        js_requires.append(conf)

    for model in js_requires:
        if not (hasattr(model, '__js_require__') or isinstance(model, dict)):
            continue
        if isinstance(model, dict):
            model_require = model
        else:
            model_require = model.__js_require__
        model_exports = model_require.pop('exports', {})
        configs.append(model_require)
        for req in model_require.get('paths', []):
            requirements.append(req)
            if req not in model_exports:
                continue
            export = model_exports[req]
            exports.append(export)
        for e, value in model_exports.items():
            if e not in requirements:
                requirements.append(e)
                exports.append(value)
    return configs, requirements, exports
