"""
Utilities for building custom models included in panel.
"""
import glob
import inspect
import io
import os
import pathlib
import shutil
import tarfile

import param
import requests

from bokeh.model import Model

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


def write_bundled_files(name, files, bundle_dir, explicit_dir=None, ext=None):
    model_name = name.split('.')[-1].lower()
    for bundle_file in files:
        bundle_file = bundle_file.split('?')[0]
        try:
            response = requests.get(bundle_file)
        except Exception:
            try:
                response = requests.get(bundle_file, verify=False)
            except Exception as e:
                print(f"Failed to fetch {name} dependency: {bundle_file}. Errored with {e}.")
                continue
        bundle_path = os.path.join(*os.path.join(*bundle_file.split('//')[1:]).split('/')[1:])
        obj_dir = explicit_dir or model_name
        filename = bundle_dir.joinpath(obj_dir, bundle_path)
        filename.parent.mkdir(parents=True, exist_ok=True)
        filename = str(filename)
        if ext and not str(filename).endswith(ext):
            filename += f'.{ext}'
        with open(filename, 'w', encoding="utf-8") as f:
            f.write(response.content.decode('utf-8'))

def write_bundled_tarball(name, tarball, bundle_dir, module=False):
    model_name = name.split('.')[-1].lower()
    try:
        response = requests.get(tarball['tar'])
    except Exception:
        response = requests.get(tarball['tar'], verify=False)
    f = io.BytesIO()
    f.write(response.content)
    f.seek(0)
    tar_obj = tarfile.open(fileobj=f)
    exclude = tarball.get('exclude', [])
    for tarf in tar_obj:
        if not tarf.name.startswith(tarball['src']) or not tarf.isfile():
            continue
        path = tarf.name.replace(tarball['src'], '')
        if any(path.startswith(exc) for exc in exclude):
            continue
        bundle_path = os.path.join(*path.split('/'))
        dest_path = os.path.join(*tarball['dest'].split('/'))
        filename = bundle_dir.joinpath(model_name, dest_path, bundle_path)
        filename.parent.mkdir(parents=True, exist_ok=True)
        fobj = tar_obj.extractfile(tarf.name)
        content = fobj.read().decode('utf-8')
        filename = str(filename)
        if module and filename.endswith('.js'):
            filename = filename[:-3]
            if filename.endswith('index'):
                filename += '.mjs'
        with open(filename, 'w', encoding="utf-8") as f:
            f.write(content)
    tar_obj.close()

            
def bundle_resources():
    from .config import panel_extension
    from .reactive import ReactiveHTML
    from .template.base import BasicTemplate
    from .template.theme import Theme

    for imp in panel_extension._imports.values():
        if imp.startswith('panel.'):
            __import__(imp)

    bundle_dir = pathlib.Path(__file__).parent.joinpath('dist', 'bundled')

    # Extract Model dependencies
    js_files = {}
    css_files = {}
    reactive = param.concrete_descendents(ReactiveHTML).values()
    models = (
        list(Model.model_class_reverse_map.items()) +
        [(f'{m.__module__}.{m.__name__}', m) for m in reactive]
    )
    for name, model in models:
        if not name.startswith('panel.'):
            continue
        prev_jsfiles = getattr(model, '__javascript_raw__', None)
        prev_jsbundle = getattr(model, '__tarball__', None)
        prev_cls = model
        for cls in model.__mro__[1:]:
            jsfiles = getattr(cls, '__javascript_raw__', None)
            if ((jsfiles is None and prev_jsfiles is not None) or
                (jsfiles is not None and jsfiles != prev_jsfiles)):
                if prev_jsbundle:
                    js_files[prev_cls.__name__] = prev_jsbundle
                else:
                    js_files[prev_cls.__name__] = prev_jsfiles
                break
            prev_cls = cls
        prev_cssfiles = getattr(model, '__css_raw__', None)
        prev_cls = model
        for cls in model.__mro__[1:]:
            cssfiles = getattr(cls, '__css_raw__', None)
            if ((cssfiles is None and prev_cssfiles is not None) or
                (cssfiles is not None and cssfiles != prev_cssfiles)):
                css_files[prev_cls.__name__] = prev_cssfiles
                break
            prev_cls = cls

    # Bundle Model dependencies
    for name, jsfiles in js_files.items():
        if isinstance(jsfiles, dict):
            write_bundled_tarball(name, jsfiles, bundle_dir)
        else:
            write_bundled_files(name, jsfiles, bundle_dir)

    for name, cssfiles in css_files.items():
        write_bundled_files(name, cssfiles, bundle_dir)

    # Bundle Template resources
    for name, template in param.concrete_descendents(BasicTemplate).items():
        # Bundle Template._resources
        if template._resources.get('bundle', True):
            write_bundled_files(name, list(template._resources.get('css', {}).values()), bundle_dir, 'css')
            write_bundled_files(name, list(template._resources.get('js', {}).values()), bundle_dir, 'js')
            js_modules = []
            for tar_name, js_module in template._resources.get('js_modules', {}).items():
                if tar_name not in template._resources.get('tarball', {}):
                    js_modules.append(js_module)
            write_bundled_files(name, js_modules, bundle_dir, 'js', ext='mjs')
            for tarball in template._resources.get('tarball', {}).values():
                write_bundled_tarball('js', tarball, bundle_dir, module=True)

        # Bundle CSS files in template dir
        template_dir = pathlib.Path(inspect.getfile(template)).parent
        dest_dir = bundle_dir / name.lower()
        dest_dir.mkdir(parents=True, exist_ok=True)
        for css in glob.glob(str(template_dir / '*.css')):
            shutil.copyfile(css, dest_dir / os.path.basename(css))

        # Bundle Template._css
        template_css = template._css
        if not isinstance(template_css, list):
            template_css = [template_css] if template_css else []
        for css in template_css:
            tmpl_name = name.lower()
            for cls in template.__mro__[1:-5]:
                tmpl_css = cls._css if isinstance(cls._css, list) else [cls._css]
                if css in tmpl_css:
                    tmpl_name = cls.__name__.lower()
            tmpl_dest_dir = bundle_dir / tmpl_name
            tmpl_dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(css, tmpl_dest_dir / os.path.basename(css))

        # Bundle Template._js
        template_js = template._js
        if not isinstance(template_js, list):
            template_js = [template_js] if template_js else []
        for js in template_js:
            tmpl_name = name.lower()
            for cls in template.__mro__[1:-5]:
                tmpl_js = cls._js if isinstance(cls._js, list) else [cls._js]
                if js in tmpl_js:
                    tmpl_name = cls.__name__.lower()
            tmpl_dest_dir = bundle_dir / tmpl_name
            shutil.copyfile(js, tmpl_dest_dir / os.path.basename(js))

    # Bundle base themes
    dest_dir = bundle_dir / 'theme'
    theme_dir = pathlib.Path(inspect.getfile(Theme)).parent
    dest_dir.mkdir(parents=True, exist_ok=True)
    for css in glob.glob(str(theme_dir / '*.css')):
        shutil.copyfile(css, dest_dir / os.path.basename(css))

    # Bundle Theme classes
    for name, theme in param.concrete_descendents(Theme).items():
        if theme.base_css:
            theme_bundle_dir = bundle_dir / theme.param.base_css.owner.__name__.lower()
            theme_bundle_dir.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(theme.base_css, theme_bundle_dir / os.path.basename(theme.base_css))
        if theme.css:
            tmplt_bundle_dir = bundle_dir / theme._template.__name__.lower()
            tmplt_bundle_dir.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(theme.css, tmplt_bundle_dir / os.path.basename(theme.css))
