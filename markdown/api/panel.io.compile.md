# panel.io.compile module

exception panel.io.compile.BuildError
Bases: `RuntimeError`

Error raised during esbuild.

panel.io.compile.compile_components(components: list\[type\[ReactiveESM\]\], build_dir: str \| PathLike \| None = None, outfile: str \| PathLike \| None = None, skip_npm: bool = False, minify: bool = True, file_loaders: list\[str\] \| None = None, verbose: bool = True) → int \| str \| None
Compiles a list of ReactiveESM components into a single JavaScript
bundle including their Javascript dependencies.

Parameters:
components : list\[type\[ReactiveESM\]\]
A list of ReactiveESM component classes to compile.

build_dir : str \| os.PathLike, optional
The directory where the build output will be saved. If None, a temporary
directory will be used.

outfile : str \| os.PathLike, optional
The path to the output file where the compiled bundle will be saved. If
None the compiled output will be returned.

**skip_npm: bool**
Whether to skip npm install (assumes build_dir is set)

minify : bool, optional
If True, minifies the compiled JavaScript bundle.

**file_loaders: list\[str\]**
List of file types (e.g. woff2 or svg) loaders to carry along

verbose : bool, optional
If True, prints detailed logs during the compilation process.

Returns:
Returns the compiled bundle or None if outfile is provided.

panel.io.compile.extract_dependencies(component: type\[ReactiveESM\]) → tuple\[str, dict\[str, Any\]\]
Extracts dependencies from a ReactiveESM component by parsing its
importmap and the associated code and replaces URL import specifiers
with package imports.

Parameters:
**component: type\[ReactiveESM\]**
The ReactiveESM component to extract a dependency definition from.

Returns:
code: str
Code where the URL imports have been replaced by package imports.

dependencies: dict\[str, str\]
A dictionary of package dependencies and their versions.

panel.io.compile.find_components(module_or_file: str \| PathLike, classes: list\[str\] \| None = None) → list\[type\[ReactiveESM\]\]
Creates a temporary module given a path-like object and finds all the
ReactiveESM components defined therein.

Parameters:
module_or_file : str \| os.PathLike
The path to the Python module.

**classes: list\[str\] \| None**
Names of classes to return.

Returns:
List of ReactiveESM components defined in the module.

panel.io.compile.find_module_bundles(module_spec: str) → dict\[Path, list\[type\[ReactiveESM\]\]\]
Takes module specifications and extracts a set of components to bundle.

Parameters:
**module_spec: str**
Module specification either as a dotted module or a path to a module.

Returns:
Dictionary containing the bundle paths and list of components to bundle.

panel.io.compile.generate_project(components: list\[type\[ReactiveESM\]\], path: str \| PathLike, project_config: dict\[str, Any\] \| None = None)
Converts a set of ESM components into a Javascript project with an
index.js, package.json and a T\|JS(X) per component.

panel.io.compile.merge_exports(old: ExportSpec, new: ExportSpec)
Appends the new exports to set of existing ones.

Appropriately combines different kinds of exports including default,
import-all exports and named exports.

panel.io.compile.packages_from_code(esm_code: str) → tuple\[str, dict\[str, str\]\]
Extracts package version definitions from ESM code.

Parameters:
esm_code : str
The ESM code to search for package imports.

Returns:
Dictionary of packages and their versions.

panel.io.compile.packages_from_importmap(esm_code: str, imports: dict\[str, str\]) → tuple\[str, dict\[str, str\]\]
Extracts package version definitions from an import map.

Parameters:
**esm_code: str**
The ESM code to replace import names in.

imports : dict\[str, str\]
A dictionary representing the import map, where keys are package names
and values are URLs.

Returns:
dict\[str, str\]
A dictionary where keys are package names and values are their
corresponding versions.

panel.io.compile.replace_imports(esm_code: str, replacements: dict\[str, str\]) → str
Replaces imports in the code which may be aliases with the actual
package names.

Parameters:
**esm_code: str**
The ESM code to replace import names in.

**replacements: dict\[str, str\]**
Mapping that defines replacements from aliased import names to actual
package names.

Returns:
modified_code: str
The code where imports have been replaced with package names.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
