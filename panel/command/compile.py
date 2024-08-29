from bokeh.command.subcommand import Argument, Subcommand

from ..io.compile import compile_module


class Compile(Subcommand):
    ''' Subcommand to generate a new encryption key.

    '''

    #: name for this subcommand
    name = "compile"

    help = "Compiles an ESM component using node and esbuild"

    args = (
        ('files', Argument(
            metavar = 'DIRECTORY-OR-SCRIPT',
            nargs   = '*',
            help    = "The app directories or scripts to serve (serve empty document if not specified)",
            default = None,
        )),
    )

    def invoke(self, args):
        for module in args.files:
            compile_module(module)
