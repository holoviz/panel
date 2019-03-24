"""
Utilities for building custom models included in panel.
"""
from __future__ import absolute_import, division, unicode_literals

import hashlib
import io
import json
import os

from bokeh.util.compiler import (AttrDict, get_cache_hook, set_cache_hook,
                                 _get_custom_models, _compile_models)

#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------

# Global variables
CUSTOM_MODELS = {}


def load_compiled_models(custom_model, implementation):
    """
    Custom hook to load cached implementation of custom models.
    """
    compiled = old_hook(custom_model, implementation)
    if compiled is not None:
        return compiled

    model = CUSTOM_MODELS.get(custom_model.full_name)
    if model is None:
        return
    ts_file = model.__implementation__
    json_file = ts_file.replace('.ts', '.json')
    if not os.path.isfile(json_file):
        return
    with io.open(ts_file, encoding="utf-8") as f:
        code = f.read()
    with io.open(json_file, encoding="utf-8") as f:
        compiled = json.load(f)
    hashed = hashlib.sha256(code.encode('utf-8')).hexdigest()
    if compiled['hash'] == hashed:
        return AttrDict(compiled)
    return None


def build_custom_models():
    """
    Compiles custom bokeh models and stores the compiled JSON alongside
    the original code.
    """
    from .config import panel_extension
    # Ensure that all optional models are loaded
    for imp in panel_extension._imports.values():
        __import__(imp)

    custom_models = _get_custom_models(list(CUSTOM_MODELS.values()))
    compiled_models = _compile_models(custom_models)
    for name, model in custom_models.items():
        compiled = compiled_models.get(name)
        if compiled is None:
            return
        print('\tBuilt %s custom model' % name)
        impl = model.implementation
        hashed = hashlib.sha256(impl.code.encode('utf-8')).hexdigest()
        compiled['hash'] = hashed
        fp = impl.file.replace('.ts', '.json')
        with open(fp, 'w') as f:
            json.dump(compiled, f)


def require_components():
    """
    Returns JS snippet to load the required dependencies in the classic
    notebook using REQUIRE JS.
    """
    from .config import config

    configs, requirements, exports = [], [], []
    js_requires = list(CUSTOM_MODELS.values())

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


old_hook = get_cache_hook()
set_cache_hook(load_compiled_models)
