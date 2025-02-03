from __future__ import annotations

import os
import pathlib
import sys

from bokeh.command.subcommand import Argument, Subcommand

from ..custom import ReactiveESM
from ..io.compile import RED, compile_components, find_module_bundles


def run_compile(
    bundles: dict[pathlib.Path, list[type[ReactiveESM]]],
    build_dir: str | os.PathLike | None = None,
    unminified: bool = False,
    skip_npm: bool = False,
    verbose: bool = False
) -> int:
    """
    Runs the compile command on the provided bundles.

    Parameters
    ----------
    bundles : dict[type[ReactiveESM]]
        A list of `ReactiveESM` component classes to compile.
    build_dir : str | os.PathLike, optional
        The directory where the build output will be saved. If None, a
        temporary directory will be used.
    outfile : str | os.PathLike, optional
        The path to the output file where the compiled bundle will be saved.
        If None the compiled output will be returned.
    skip_npm: bool
        Whether to skip npm install (assumes build_dir is set)
    minify : bool, optional
        If True, minifies the compiled JavaScript bundle.
    verbose : bool, optional
        If True, prints detailed logs during the compilation process.

    Returns
    -------
    int:
       Count of errors.
    """
    errors = 0
    for bundle, components in bundles.items():
        component_names = '\n- '.join(c.name for c in components)
        print(f"Building {bundle} containing the following components:\n\n- {component_names}\n")  # noqa
        out = compile_components(
            components,
            build_dir=build_dir,
            minify=not unminified,
            outfile=bundle,
            skip_npm=skip_npm,
            verbose=verbose,
        )
        if not out:
            errors += 1
    return errors


class Compile(Subcommand):
    ''' Subcommand to generate a new encryption key.

    '''

    #: name for this subcommand
    name = "compile"

    help = "Compiles an ESM component using node and esbuild"

    args = (
        ('modules', Argument(
            metavar = 'DIRECTORY-OR-SCRIPT',
            nargs   = "*",
            help    = "The Python modules to compile. May optionally define a single class.",
            default = None,
        )),
        ('--build-dir', Argument(
            action = 'store',
            type    = str,
            help    = "Where to write the build directory."
        )),
        ('--skip-npm', Argument(
            action  = 'store_true',
            help    = "Whether to skip npm install step (only possible if build_dir with existing node_modules is available)."
        )),
        ('--unminified', Argument(
            action  = 'store_true',
            help    = "Whether to generate unminified output."
        )),
        ('--verbose', Argument(
            action  = 'store_true',
            help    = "Whether to show verbose output. Note when setting --outfile only the result will be printed to stdout."
        )),
        ('--watch', Argument(
            action  = 'store_true',
            help    = 'Whether to watch the input files for changes and recompile the bundle.'
        )),
    )

    def invoke(self, args):
        bundles = {}
        for module in args.modules:
            try:
                module_bundles = find_module_bundles(module)
            except RuntimeError as e:
                print(f'{RED} {e}')  # noqa
                return 1
            if not module_bundles:
                print (  # noqa
                    f'{RED} Could not find any ESM components to compile '
                    f'in {module}, ensure you provided the right module.'
                )
            for bundle, components in module_bundles.items():
                if bundle in bundles:
                    bundles[bundle] += components
                else:
                    bundles[bundle] = components

        errors = run_compile(bundles, args.build_dir, args.unminified, args.skip_npm, args.verbose)
        if args.watch:
            from watchfiles import watch
            paths_to_watch = set()
            for _, components in bundles.items():
                for component in components:
                    mod = sys.modules[component.__module__]
                    mod_path = pathlib.Path(mod.__file__)
                    paths_to_watch.add(mod_path)
                    paths_to_watch.add(mod_path.parent / component._esm_path(compiled=False))
            for _changes in watch(*paths_to_watch):
                errors = run_compile(bundles, args.build_dir, args.unminified, args.skip_npm, args.verbose)
        return int(errors>0)
