import os
import pathlib
import sys

from collections import defaultdict

from bokeh.command.subcommand import Argument, Subcommand

from ..io.compile import RED, compile_components, find_components


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
        ('--build-dir', dict(
            action = 'store',
            type    = str,
            help    = "Where to write the build directory."
        )),
        ('--unminified', dict(
            action  = 'store_true',
            help    = "Whether to generate unminified output."
        )),
        ('--verbose', dict(
            action  = 'store_true',
            help    = "Whether to show verbose output. Note when setting --outfile only the result will be printed to stdout."
        )),
    )

    def invoke(self, args):
        bundles = defaultdict(list)
        for module_spec in args.modules:
            if ':' in module_spec:
                *parts, cls = module_spec.split(':')
                module = ':'.join(parts)
            else:
                module = module_spec
                cls = ''
            classes = cls.split(',') if cls else None
            module_name, ext = os.path.splitext(os.path.basename(module))
            if ext not in ('', '.py'):
                print(  # noqa
                    f'{RED} Can only compile ESM components defined in Python '
                    'file or importable module.'
                )
                return 1
            try:
                components = find_components(module, classes)
            except ValueError:
                cls_error = f' and that class(es) {cls!r} are defined therein' if cls else ''
                print(  # noqa
                    f'{RED} Could not find any ESM components to compile, ensure '
                    f'you provided the right module{cls_error}.'
                )
                return 1
            if module in sys.modules:
                module_path = sys.modules[module].__file__
            else:
                module_path = module
            module_path = pathlib.Path(module_path).parent
            for component in components:
                if component._bundle:
                    bundle_path = component._bundle
                    if isinstance(bundle_path, str):
                        path = (module_path / bundle_path).absolute()
                    else:
                        path = bundle_path.absolute()
                    bundles[str(path)].append(component)
                elif len(components) > 1 and not classes:
                    component_module = module_name if ext else component.__module__
                    bundles[module_path / f'{component_module}.bundle.js'].append(component)
                else:
                    bundles[module_path / f'{component.__name__}.bundle.js'].append(component)

        errors = 0
        for bundle, components in bundles.items():
            out = compile_components(
                components,
                build_dir=args.build_dir,
                minify=not args.unminified,
                outfile=bundle,
                verbose=args.verbose,
            )
            if not out:
                errors += 1
        return int(errors>0)
