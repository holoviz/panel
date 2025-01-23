from __future__ import annotations

import fnmatch
import importlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

from collections import defaultdict
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

from bokeh.application.handlers.code_runner import CodeRunner

from ..custom import ReactComponent, ReactiveESM

if TYPE_CHECKING:
    from ..custom import ExportSpec


GREEN, RED, RESET = "\033[0;32m", "\033[0;31m", "\033[0m"

# Regex pattern to match import statements with URLs starting with https
_ESM_IMPORT_RE = re.compile(
    r'import\s+.*?\s+from\s+["\']'     # Match 'import ... from' with any content
    r'(https:\/\/[^\/]+\/(?:npm\/)?'   # Match the base URL (e.g., https://cdn.jsdelivr.net/) and ignore /npm if present
    r'((?:@[\w\.\-]+\/)?[\w\.\-]+)'    # Capture the package name, including optional scope
    r'(?:@([\d\.\w-]+))?'              # Optionally capture the version after @
    r'[^"\']*)["\']'                   # Match the rest of the URL up to the quote
)
_ESM_IMPORT_SUFFIX = re.compile(r'\/([^?"&\']*)')

# Regex pattern to extract version specifiers from a URL
_ESM_URL_RE = re.compile(
    r'(https:\/\/[^\/]+\/(?:npm\/)?'
    r'((?:@[\w\.\-]+\/)?[\w\.\-]+)'
    r'(?:@([\d\.\w-]+))?'
    r'[^"\']*)'
)
_ESM_IMPORT_ALIAS_RE = re.compile(r'(import\s+(?:\*\s+as\s+\w+|\{[^}]*\}|[\w*\s,]+)\s+from\s+[\'"])(.*?)([\'"])')
_EXPORT_DEFAULT_RE = re.compile(r'\bexport\s+default\b')


@contextmanager
def setup_build_dir(build_dir: str | os.PathLike | None = None):
    original_directory = os.getcwd()
    if build_dir:
        temp_dir = pathlib.Path(build_dir).absolute()
        temp_dir.mkdir(parents=True, exist_ok=True)
    else:
        temp_dir = pathlib.Path(tempfile.mkdtemp())
    try:
        os.chdir(temp_dir)
        yield temp_dir
    finally:
        os.chdir(original_directory)
        if not build_dir:
            shutil.rmtree(temp_dir)


def check_cli_tool(tool_name: str) -> bool:
    try:
        cmd = shutil.which(tool_name)
    except Exception:
        cmd = None
    if cmd:
        return True
    if sys.platform == 'win32':
        tool_name = f'{tool_name}.cmd'
        return check_cli_tool(tool_name)
    return False


def find_module_bundles(module_spec: str) -> dict[pathlib.Path, list[ReactiveESM]]:
    """
    Takes module specifications and extracts a set of components to bundle.

    Parameters
    ----------
    module_spec: str
         Module specification either as a dotted module or a path to a module.

    Returns
    -------
    Dictionary containing the bundle paths and list of components to bundle.
    """
    # Split module spec, while respecting Windows drive letters
    if ':' in module_spec and (module_spec[1:3] != ':\\' or module_spec.count(':') > 1):
        module, cls = module_spec.rsplit(':', 1)
    else:
        module = module_spec
        cls = ''
    classes = cls.split(',') if cls else None
    if module.endswith('.py'):
        module_name, _ = os.path.splitext(os.path.basename(module))
    else:
        module_name = module
    try:
        components = find_components(module, classes)
    except ValueError:
        cls_error = f' and that class(es) {cls!r} are defined therein' if cls else ''
        raise RuntimeError(  # noqa
            f'Could not find any ESM components to compile, ensure '
            f'you provided the right module{cls_error}.'
        )
    if module in sys.modules:
        module_file = sys.modules[module].__file__
    else:
        module_file = module
    assert module_file is not None

    bundles = defaultdict(list)
    module_path = pathlib.Path(module_file).parent
    for component in components:
        if component._bundle:
            bundle_path = component._bundle
            if isinstance(bundle_path, str):
                path = (module_path / bundle_path).absolute()
            else:
                path = bundle_path.absolute()
            bundles[path].append(component)
        elif len(components) > 1 and not classes:
            component_module = module_name or component.__module__
            bundles[module_path / f'{component_module}.bundle.js'].append(component)
        else:
            bundles[component._module_path / f'{component.__name__}.bundle.js'].append(component)

    return dict(bundles)


def find_components(module_or_file: str | os.PathLike, classes: list[str] | None = None) -> list[type[ReactiveESM]]:
    """
    Creates a temporary module given a path-like object and finds all
    the ReactiveESM components defined therein.

    Parameters
    ----------
    module_or_file : str | os.PathLike
        The path to the Python module.
    classes: list[str] | None
        Names of classes to return.

    Returns
    -------
    List of ReactiveESM components defined in the module.
    """
    py_file = str(module_or_file).endswith('.py')
    if py_file:
        path_obj = pathlib.Path(module_or_file)
        source = path_obj.read_text(encoding='utf-8')
        runner = CodeRunner(source, module_or_file, [])
        module = runner.new_module()
        assert module is not None
        runner.run(module)
        if runner.error:
            raise RuntimeError(
                f'Compilation failed because supplied module errored on import:\n\n{runner.error}'
            )
    else:
        module = importlib.import_module(str(module_or_file))
    classes = classes or []
    components = []
    for v in module.__dict__.values():
        if (
            isinstance(v, type) and
            issubclass(v, ReactiveESM) and
            not v.abstract and
            (not classes or any(fnmatch.fnmatch(v.__name__, p) for p in classes))
        ):
            if py_file:
                v.__path__ = path_obj.parent.absolute()
            components.append(v)
    not_found = {cls for cls in classes if '*' not in cls} - {c.__name__ for c in components}
    if classes and not_found:
        clss = ', '.join(map(repr, not_found))
        raise ValueError(f'{clss} class(es) not found in {module_or_file!r}.')
    return components


def packages_from_code(esm_code: str) -> tuple[str, dict[str, str]]:
    """
    Extracts package version definitions from ESM code.

    Parameters
    ----------
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
        import_name = package_name
        if after_slash_match:
            suffix = after_slash_match.group(1)
            if suffix != '+esm' and not suffix.endswith(('.js', '.mjs')):
                # ESM specifier is used by some CDNs to load ESM bundle
                import_name += f'/{suffix}'
        esm_code = esm_code.replace(url, import_name)
    return esm_code, packages


def replace_imports(esm_code: str, replacements: dict[str, str]) -> str:
    """
    Replaces imports in the code which may be aliases with the actual
    package names.

    Parameters
    ----------
    esm_code: str
        The ESM code to replace import names in.
    replacements: dict[str, str]
        Mapping that defines replacements from aliased import names
        to actual package names.

    Returns
    -------
    modified_code: str
        The code where imports have been replaced with package names.
    """

    def replace_match(match):
        import_part = match.group(1)
        module_path = match.group(2)
        quote = match.group(3)
        for old, new in replacements.items():
            if module_path.startswith(old):
                module_path = module_path.replace(old, new, 1)
                break
        return f"{import_part}{module_path}{quote}"

    # Use the sub method to replace the matching parts of the import statements
    modified_code = _ESM_IMPORT_ALIAS_RE.sub(replace_match, esm_code)
    return modified_code


def packages_from_importmap(esm_code: str, imports: dict[str, str]) -> tuple[str, dict[str, str]]:
    """
    Extracts package version definitions from an import map.

    Parameters
    ----------
    esm_code: str
        The ESM code to replace import names in.
    imports : dict[str, str]
        A dictionary representing the import map, where keys are package names and values are URLs.

    Returns
    -------
    dict[str, str]
        A dictionary where keys are package names and values are their corresponding versions.
    """
    dependencies, replacements = {}, {}
    for key, url in imports.items():
        match = _ESM_URL_RE.search(url)
        if not match:
            raise RuntimeError(
                f'Could not determine package name from URL: {url!r}.'
            )
        pkg_name = match.group(2)
        version = match.group(3)
        dependencies[pkg_name] = f"^{version}" if version else "latest"
        replacements[key] = pkg_name+'/' if key.endswith('/') else pkg_name
    esm_code = replace_imports(esm_code, replacements)
    return esm_code, dependencies


def extract_dependencies(component: type[ReactiveESM]) -> tuple[str, dict[str, Any]]:
    """
    Extracts dependencies from a ReactiveESM component by parsing its
    importmap and the associated code and replaces URL import
    specifiers with package imports.

    Parameters
    ----------
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
    esm = component._render_esm(compiled='compiling')
    esm, dependencies = packages_from_importmap(esm, importmap.get('imports', {}))
    esm, packages = packages_from_code(esm)
    dependencies.update(packages)
    return esm, dependencies


def merge_exports(old: ExportSpec, new: ExportSpec):
    """
    Appends the new exports to set of existing ones.

    Appropriately combines different kinds of exports including
    default, import-all exports and named exports.
    """
    for export, specs in new.items():
        if export not in old:
            old[export] = list(specs)
            continue
        prev = old[export]
        for spec in specs:
            if isinstance(spec, tuple):
                for i, p in enumerate(prev):
                    if isinstance(p, tuple):
                        prev[i] = tuple(dict.fromkeys(p+spec))
                        break
                else:
                    prev.append(spec)
            elif spec not in prev:
                prev.append(spec)


def generate_index(imports: str, exports: list[str], export_spec: ExportSpec):
    index_js = imports
    exports = list(exports)
    for module, specs in export_spec.items():
        for spec in specs:
            # TODO: Handle name clashes in exports
            if isinstance(spec, tuple):
                imports = f"{{{', '.join(spec)}}}"
                exports.extend(spec)
            elif spec.startswith('*'):
                imports = f"* as {spec[1:]}"
                exports.append(spec[1:])
            else:
                imports = spec
                exports.append(spec)
            index_js += f'import {imports} from "{module}"\n'

    export_string = ', '.join(exports)
    index_js += f"export default {{{export_string}}}"
    return index_js


def generate_project(
    components: list[type[ReactiveESM]],
    path: str | os.PathLike,
    project_config: dict[str, Any] | None = None
):
    """
    Converts a set of ESM components into a Javascript project with
    an index.js, package.json and a T|JS(X) per component.
    """
    path = pathlib.Path(path)
    component_names = []
    dependencies = {}
    export_spec: ExportSpec = {}
    index = ''
    for component in components:
        name = component.__name__
        esm_path = component._esm_path(compiled=False)
        if esm_path:
            ext = esm_path.suffix.lstrip('.')
        else:
            ext = 'jsx' if issubclass(component, ReactComponent) else 'js'
        code, component_deps = extract_dependencies(component)
        # Detect default export in component code and handle import accordingly
        if _EXPORT_DEFAULT_RE.search(code):
            index += f'import {name} from "./{name}"\n'
        else:
            index += f'import * as {name} from "./{name}"\n'

        with open(path / f'{name}.{ext}', 'w') as component_file:
            component_file.write(code)
        # TODO: Improve merging of dependencies
        dependencies.update(component_deps)
        merge_exports(export_spec, component._exports__)
        component_names.append(name)

    # Create package.json and write to temp directory
    package_json = {"dependencies": dependencies}
    if project_config:
        package_json.update(project_config)
    with open(path / 'package.json', 'w') as package_json_file:
        json.dump(package_json, package_json_file, indent=2)

    # Generate index file from component imports, exports and export specs
    index_js = generate_index(index, component_names, export_spec)
    with open(path / 'index.js', 'w') as index_js_file:
        index_js_file.write(index_js)


def compile_components(
    components: list[type[ReactiveESM]],
    build_dir: str | os.PathLike | None = None,
    outfile: str | os.PathLike | None = None,
    minify: bool = True,
    verbose: bool = True
) -> int | str | None:
    """
    Compiles a list of ReactiveESM components into a single JavaScript bundle
    including their Javascript dependencies.

    Parameters
    ----------
    components : list[type[ReactiveESM]]
        A list of `ReactiveESM` component classes to compile.
    build_dir : str | os.PathLike, optional
        The directory where the build output will be saved. If None, a
        temporary directory will be used.
    outfile : str | os.PathLike, optional
        The path to the output file where the compiled bundle will be saved.
        If None the compiled output will be returned.
    minify : bool, optional
        If True, minifies the compiled JavaScript bundle.
    verbose : bool, optional
        If True, prints detailed logs during the compilation process.

    Returns
    -------
    Returns the compiled bundle or None if outfile is provided.
    """
    npm_cmd = 'npm.cmd' if sys.platform == 'win32' else 'npm'
    if not check_cli_tool(npm_cmd):
        raise RuntimeError(
            'Could not find `npm` or it generated an error. Ensure it is '
            'installed and can be run with `npm --version`. You can get it '
            'with conda or you favorite package manager or nodejs manager.'
        )
    if not check_cli_tool('esbuild'):
        raise RuntimeError(
            'Could not find `esbuild` or it generated an error. Ensure it '
            'is installed and can be run with `esbuild --version`. You can '
            'install it with conda or with `npm install -g esbuild`.'
        )

    out = str(pathlib.Path(outfile).absolute()) if outfile else None
    with setup_build_dir(build_dir) as out_dir:
        generate_project(components, out_dir)
        extra_args = []
        if verbose:
            extra_args.append('--log-level=debug')
        install_cmd = [npm_cmd, 'install'] + extra_args
        try:
            if out:
                print(f"Running command: {' '.join(install_cmd)}\n")  # noqa
            result = subprocess.run(install_cmd, check=True, capture_output=True, text=True)
            if result.stdout and out:
                print(f"npm output:\n{GREEN}{result.stdout}{RESET}")  # noqa
            if result.stderr:
                print(f"npm errors:\n{RED}{result.stderr}{RESET}")  # noqa

        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running npm install:\n{RED}{e.stderr}{RESET}")  # noqa
            return None

        if any(issubclass(c, ReactComponent) for c in components):
            extra_args.append('--loader:.js=jsx')
        if minify:
            extra_args.append('--minify')
        if out:
            extra_args.append(f'--outfile={out}')
        build_cmd = ['esbuild', 'index.js', '--bundle', '--format=esm'] + extra_args
        try:
            if verbose:
                print(f"Running command: {' '.join(build_cmd)}\n")  # noqa
            result = subprocess.run(build_cmd+['--color=true'], check=True, capture_output=True, text=True)
            if result.stderr:
                print(f"esbuild output:\n{result.stderr}")  # noqa
                return None
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running esbuild: {e.stderr}")  # noqa
            return None
        return 0 if outfile else result.stdout
