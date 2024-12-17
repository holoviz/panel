from bokeh.command.subcommand import Argument, Subcommand

from ..io.compile import RED, compile_components, find_module_bundles


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
        ('--unminified', Argument(
            action  = 'store_true',
            help    = "Whether to generate unminified output."
        )),
        ('--verbose', Argument(
            action  = 'store_true',
            help    = "Whether to show verbose output. Note when setting --outfile only the result will be printed to stdout."
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

        errors = 0
        for bundle, components in bundles.items():
            component_names = '\n- '.join(c.name for c in components)
            print(f"Building {bundle} containing the following components:\n\n- {component_names}\n")  # noqa
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
