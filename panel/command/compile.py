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
        ('--outfile', dict(
            action = 'store',
            type    = str,
            help    = "File to write the bundle to."
        )),
        ('--unminify', dict(
            action  = 'store_true',
            help    = "Whether to generate unminified output."
        )),
        ('--verbose', dict(
            action  = 'store_true',
            help    = "Whether to show verbose output. Note when setting --outfile only the result will be printed to stdout."
        )),
    )

    def invoke(self, args):
        components = []
        for module_spec in args.modules:
            if '.py:' in module_spec:
                *parts, cls = module_spec.split(':')
                module = ':'.join(parts)
            elif not module_spec.endswith('.py'):
                print(  # noqa
                    f'{RED} Can only compile ESM components defined in a Python '
                    'module, ensure you provide a file with a .py extension.'
                )
                return 1
            else:
                module = module_spec
                cls = None
            try:
                components += find_components(module, cls)
            except ValueError:
                cls_error = f' and that class {cls!r} is defined therein' if cls else ''
                print(  # noqa
                    f'{RED} Could not find any ESM components to compile, ensure '
                    f'you provided the right module{cls_error}.'
                )
                return 1
        out = compile_components(
            components,
            build_dir=args.build_dir,
            minify=not args.unminify,
            outfile=args.outfile,
            verbose=args.verbose and args.outfile,
        )
        if args.outfile:
            if not out == 0:
                return 1
        elif out is None:
            return 1
        else:
            print(out)  # noqa
        return 0
