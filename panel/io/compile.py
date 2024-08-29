import inspect
import json
import os
import pathlib
import re
import subprocess
import tempfile

from bokeh.application.handlers.code_runner import CodeRunner

from ..custom import ReactComponent, ReactiveESM
from ..util import camel_to_kebab

# Regex pattern to match import statements with URLs starting with https
_ESM_IMPORT_RE = re.compile(r'import\s+.*?\s+from\s+["\'](https:\/\/[^\/]+\/([^@\/]+)(?:@([\d\.\w-]+))?[^"\']*)["\']'
)
_ESM_IMPORT_SUFFIX = re.compile(r'\/([^?"&\']*)')

# Regex pattern to extract version specifiers from a URL
_ESM_VERSION_RE = re.compile(r'@(\d+\.\d+\.\d+(-[a-zA-Z]+(\.\d+)?)?)')


def find_components(path: str | os.PathLike) -> list[type[ReactiveESM]]:
    """
    Creates a temporary module given a path-like object and finds all
    the ReactiveESM components defined therein.

    Arguments
    ---------
    path : str | os.PathLike
        The path to the Python module.

    Returns
    -------
    List of ReactiveESM components defined in the module.
    """
    path_obj = pathlib.Path(path)
    source = path_obj.read_text(encoding='utf-8')
    runner = CodeRunner(source, path, [])
    module = runner.new_module()
    runner.run(module)
    components = []
    for v in module.__dict__.values():
        if isinstance(v, type) and issubclass(v, ReactiveESM) and not v.abstract:
            v.__path__ = path_obj.parent.absolute()
            components.append(v)
    return components


def packages_from_code(esm_code: str) -> dict[str, str]:
    """
    Extracts package version definitions from ESM code.

    Arguments
    ---------
    esm_code : str
        The ESM code to search for package imports.

    Returns
    -------
    Dictionary of packages and their versions.
    """
    packages = {}
    for match in _ESM_IMPORT_RE.findall(esm_code):
        url, package_name, version = match
        packages[package_name] = f'^{version}'
        after_slash_match = _ESM_IMPORT_SUFFIX.search(url.split('@')[-1])
        if after_slash_match:
            suffix = after_slash_match.group(1)
            import_name = f'{package_name}/{suffix}'
        else:
            import_name = package_name
        esm_code = esm_code.replace(url, import_name)

    return esm_code, packages


def packages_from_importmap(imports: dict[str, str]) -> dict[str, str]:
    """
    Extracts package version definitions from an import map.

    Arguments
    ---------
    imports : dict[str, str]
        A dictionary representing the import map, where keys are package names and values are URLs.

    Returns
    -------
    dict[str, str]
        A dictionary where keys are package names and values are their corresponding versions.
    """
    dependencies = {}
    for key, url in imports.items():
        match = _ESM_VERSION_RE.search(url)
        if key.endswith('/'):
            key = key[:-1]

        if match:
            dependencies[key] = f"^{match.group(1)}"
        else:
            dependencies[key] = "latest"
    return dependencies


def extract_dependencies(component: type[ReactiveESM]) -> tuple[str, dict[str, any]]:
    """
    Extracts dependencies from a ReactiveESM component by parsing its
    importmap and the associated code and replaces URL import
    specifiers with package imports.

    Arguments
    ---------
    component: type[ReactiveESM]
        The ReactiveESM component to extract a dependency definition from.

    Returns
    -------
    code: str
        Code where the URL imports have been replaced by package imports.
    dependencies: dict[str, str]
        A dictionary of package dependencies and their versions.
    """
    importmap = component._process_importmap()
    if not importmap:
        raise ValueError(
            f'{component.__name__} did not declare an importmap '
            'and cannot be compiled.'
        )

    dependencies = packages_from_importmap(importmap.get('imports', {}))
    esm = component._render_esm(compiled=False)
    if issubclass(component, ReactComponent):
        esm += '\nimport * as React from "react"\nimport { createRoot } from "react-dom/client"\nexport default {render, React, createRoot}'
    js_code, packages = packages_from_code(esm)
    dependencies.update(packages)

    # Create package.json structure
    package_json = {
        "name": camel_to_kebab(component.__name__),
        "dependencies": dependencies
    }
    return js_code, package_json


def compile_component(component: type[ReactiveESM], minify: bool = True):
    """
    Compiles and bundles the ESM code of a ReactiveESM component and
    writes the compiled JS file to a file adjacent to the module
    the component was defined in.
    """
    name = camel_to_kebab(component.__name__)
    ext = 'jsx' if issubclass(component, ReactComponent) else 'js'
    if hasattr(component, '__path__'):
        out_path = component.__path__
    else:
        out_path = pathlib.Path(inspect.getfile(component)).parent
    out = (out_path / f'{name}.compiled.js').absolute()

    code, package_json = extract_dependencies(component)

    with tempfile.TemporaryDirectory() as temp_dir:
        package_json_path = os.path.join(temp_dir, 'package.json')
        with open(package_json_path, 'w') as package_json_file:
            json.dump(package_json, package_json_file, indent=2)

        index_js_path = os.path.join(temp_dir, f'index.{ext}')
        with open(index_js_path, 'w') as index_js_file:
            index_js_file.write(code)

        os.chdir(temp_dir)

        install_cmd = ['npm', 'install']
        try:
            print(f"Running command: {' '.join(install_cmd)}")  # noqa
            result = subprocess.run(install_cmd, check=True, capture_output=True, text=True)
            if result.stdout:
                print("npm output:", result.stdout)  # noqa
            if result.stderr:
                print("npm errors:", result.stderr)  # noqa
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running npm install: {e.stderr}")  # noqa

        minify_arg = ['--minify'] if minify else []
        build_cmd = ['esbuild', index_js_path, '--bundle', '--format=esm', f'--outfile={out}'] + minify_arg
        try:
            print(f"Running command: {' '.join(build_cmd)}")  # noqa
            result = subprocess.run(build_cmd, check=True, capture_output=True, text=True)
            if result.stderr:
                print("esbuild output:", result.stderr)  # noqa
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running esbuild: {e.stderr}")  # noqa


def compile_module(module: str | os.PathLike, minify: bool = True):
    for component in find_components(module):
        compile_component(component, minify=minify)
