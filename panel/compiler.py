"""
Utilities for building custom models included in panel.
"""
import fnmatch
import glob
import inspect
import io
import os
import pathlib
import shutil
import tarfile
import zipfile

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
    from .reactive import ReactiveHTML

    configs, requirements, exports = [], [], {}
    js_requires = []

    from bokeh.model import Model
    for qual_name, model in Model.model_class_reverse_map.items():
        # We need to enable Models from Panel as well as Panel extensions
        # like awesome_panel_extensions.
        # The Bokeh models do not have "." in the qual_name
        if "." in qual_name:
            js_requires.append(model)

    js_requires += list(param.concrete_descendents(ReactiveHTML).values())

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
            model_require = dict(model.__js_require__)

        model_exports = model_require.pop('exports', {})
        if not any(model_require == config for config in configs):
            configs.append(model_require)

        for req in list(model_require.get('paths', [])):
            if isinstance(req, tuple):
                model_require['paths'] = dict(model_require['paths'])
                model_require['paths'][req[0]] = model_require['paths'].pop(req)

            reqs = req[1] if isinstance(req, tuple) else (req,)
            for r in reqs:
                if r not in requirements:
                    requirements.append(r)
                    if r in model_exports:
                        exports[r] = model_exports[r]

    return configs, requirements, exports, skip_import

def write_bundled_files(name, files, bundle_dir, explicit_dir=None, ext=None):
    from .config import config

    model_name = name.split('.')[-1].lower()
    for bundle_file in files:
        bundle_file = bundle_file.split('?')[0]
        try:
            response = requests.get(bundle_file)
        except Exception:
            try:
                response = requests.get(bundle_file, verify=False)
            except Exception as e:
                raise ConnectionError(
                    f"Failed to fetch {name} dependency: {bundle_file}. Errored with {e}."
                )
        try:
            map_file = f'{bundle_file}.map'
            map_response = requests.get(map_file)
        except Exception:
            try:
                map_response = requests.get(map_file, verify=False)
            except Exception:
                map_response = None
        if bundle_file.startswith(config.npm_cdn):
            bundle_path = os.path.join(*bundle_file.replace(config.npm_cdn, '').split('/'))
        else:
            bundle_path = os.path.join(*os.path.join(*bundle_file.split('//')[1:]).split('/')[1:])
        obj_dir = explicit_dir or model_name
        filename = bundle_dir.joinpath(obj_dir, bundle_path)
        filename.parent.mkdir(parents=True, exist_ok=True)
        filename = str(filename)
        if ext and not str(filename).endswith(ext):
            filename += f'.{ext}'
        if filename.endswith('.ttf'):
            with open(filename, 'wb') as f:
                f.write(response.content)
        else:
            content = response.content.decode('utf-8')
            with open(filename, 'w', encoding="utf-8") as f:
                f.write(content)
        if map_response:
            with open(f'{filename}.map', 'w', encoding="utf-8") as f:
                f.write(map_response.content.decode('utf-8'))

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
        if any(fnmatch.fnmatch(tarf.name, exc) for exc in exclude):
            continue
        bundle_path = os.path.join(*path.split('/'))
        dest_path = tarball['dest'].replace('/', os.path.sep)
        filename = bundle_dir.joinpath(model_name, dest_path, bundle_path)
        filename.parent.mkdir(parents=True, exist_ok=True)
        fobj = tar_obj.extractfile(tarf.name)
        filename = str(filename)
        if module and filename.endswith('.js'):
            filename = filename[:-3]
            if filename.endswith('index'):
                filename += '.mjs'
        if any(filename.endswith(ft) for ft in ('.ttf', '.eot', '.woff', '.woff2')):
            content = fobj.read()
            with open(filename, 'wb') as f:
                f.write(content)
        else:
            content = fobj.read().decode('utf-8')
            with open(filename, 'w', encoding="utf-8") as f:
                f.write(content)
    tar_obj.close()

def write_bundled_zip(name, resource, bundle_dir):
    try:
        response = requests.get(resource['zip'])
    except Exception:
        response = requests.get(resource['zip'], verify=False)
    f = io.BytesIO()
    f.write(response.content)
    f.seek(0)
    zip_obj = zipfile.ZipFile(f)
    exclude = resource.get('exclude', [])
    for zipf in zip_obj.namelist():
        path = zipf.replace(resource['src'], '')
        if any(fnmatch.fnmatch(zipf, exc) for exc in exclude) or zipf.endswith('/'):
            continue
        bundle_path = path.replace('/', os.path.sep)
        filename = bundle_dir.joinpath(name, bundle_path)
        filename.parent.mkdir(parents=True, exist_ok=True)
        fdata = zip_obj.read(zipf)
        filename = str(filename)
        if any(filename.endswith(ft) for ft in ('.ttf', '.eot', '.woff', '.woff2')):
            with open(filename, 'wb') as f:
                f.write(fdata)
        else:
            with open(filename, 'w', encoding="utf-8") as f:
                f.write(fdata.decode('utf-8'))
    zip_obj.close()

def bundle_resources(verbose=False):
    from .config import panel_extension
    from .io.resources import RESOURCE_URLS
    from .reactive import ReactiveHTML
    from .template.base import BasicTemplate
    from .template.theme import Theme

    for imp in panel_extension._imports.values():
        if imp.startswith('panel.'):
            __import__(imp)

    bundle_dir = pathlib.Path(__file__).parent.joinpath('dist', 'bundled')

    # Collect shared resources
    for name, resource in RESOURCE_URLS.items():
        if verbose:
            print(f'Bundling shared resource {name}.')
        if 'zip' in resource:
            write_bundled_zip(name, resource, bundle_dir)
        elif 'tar' in resource:
            write_bundled_tarball(name, resource, bundle_dir)

    # Extract Model dependencies
    js_files, css_files, resource_files = {}, {}, {}
    reactive = param.concrete_descendents(ReactiveHTML).values()
    models = (
        list(Model.model_class_reverse_map.items()) +
        [(f'{m.__module__}.{m.__name__}', m) for m in reactive]
    )
    for name, model in models:
        if not name.startswith('panel.'):
            continue
        if verbose:
            print(f'Collecting {name} resources')
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
        prev_resources = getattr(model, '__resources__', None)
        prev_cls = model
        for cls in model.__mro__[1:]:
            resources = getattr(cls, '__resources__', None)
            if ((resources is None and prev_resources is not None) or
                (resources is not None and resources != prev_resources)):
                resource_files[prev_cls.__name__] = prev_resources
                break
            prev_cls = cls

    # Bundle Model dependencies
    for name, jsfiles in js_files.items():
        if verbose:
            print(f'Bundling {name} model JS resources')
        if isinstance(jsfiles, dict):
            write_bundled_tarball(name, jsfiles, bundle_dir)
        else:
            write_bundled_files(name, jsfiles, bundle_dir)

    for name, cssfiles in css_files.items():
        if verbose:
            print(f'Bundling {name} model CSS resources')
        write_bundled_files(name, cssfiles, bundle_dir)

    for name, res_files in resource_files.items():
        write_bundled_files(name, res_files, bundle_dir)

    # Bundle Template resources
    for name, template in param.concrete_descendents(BasicTemplate).items():
        if verbose:
            print(f'Bundling {name} resources')
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
                write_bundled_tarball('js', tarball, bundle_dir)

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
        if verbose:
            print(f'Bundling {name} theme resources')
        if theme.base_css:
            theme_bundle_dir = bundle_dir / theme.param.base_css.owner.__name__.lower()
            theme_bundle_dir.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(theme.base_css, theme_bundle_dir / os.path.basename(theme.base_css))
        if theme.css:
            tmplt_bundle_dir = bundle_dir / theme._template.__name__.lower()
            tmplt_bundle_dir.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(theme.css, tmplt_bundle_dir / os.path.basename(theme.css))

    # Bundle icons & images
    dest_dir = bundle_dir / 'images'
    dest_dir.mkdir(parents=True, exist_ok=True)
    icon_dir = pathlib.Path(__file__).parent.parent / 'doc' / '_static' / 'icons'
    for icon in glob.glob(str(icon_dir / '*')):
        shutil.copyfile(icon, dest_dir / os.path.basename(icon))
