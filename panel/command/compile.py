from bokeh.command.subcommand import Argument, Subcommand

from ..io.compile import RED, compile_component, find_components


class Compile(Subcommand):
    ''' Subcommand to generate a new encryption key.

    '''

    #: name for this subcommand
    name = "compile"

    help = "Compiles an ESM component using node and esbuild"

    args = (
        ('module', Argument(
            metavar = 'DIRECTORY-OR-SCRIPT',
            nargs   = 1,
            help    = "The Python module to compile. May optionally define a single class.",
            default = None,
        )),
        ('--unminify', dict(
            action  = 'store_true',
            help    = "Whether to generate unminified output."
        )),
        ('--verbose', dict(
            action  = 'store_true',
            help    = "Whether to print progress"
        )),
    )

    def invoke(self, args):
        module_spec = args.module[0]
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
        components = find_components(module)
        compiled, errors = 0, 0
        for component in components:
            if cls is not None and component.__name__ != cls:
                continue
            errors += compile_component(component, minify=not args.unminify, verbose=args.verbose)
            compiled += 1
        if not compiled:
            cls_error = f' and that class {cls!r} is defined therein' if cls else ''
            print(  # noqa
                f'{RED} Could not find any ESM components to compile, ensure '
                f'you provided the right module{cls_error}.'
            )
            return 1
        return 1 if errors else 0
