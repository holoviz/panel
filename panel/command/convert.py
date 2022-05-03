import argparse
import os

from bokeh.command.subcommand import Argument, Subcommand

from ..io.convert import script_to_html


class Convert(Subcommand):
    ''' Subcommand to convert Panel application to some build target, e.g. pyodide or pyscript.

    '''

    #: name for this subcommand
    name = "convert"

    help = "Convert a Panel App to another format, e.g. a HTML file."

    args = (
        ('files', Argument(
            metavar = 'DIRECTORY-OR-SCRIPT',
            nargs   = '*',
            help    = "The app directories or scripts to serve (serve empty document if not specified)",
            default = None,
        )),
        ('--to', dict(
            action  = 'store',
            type    = str,
            help    = "The format to convert to.",
        )),
        ('--prerender', dict(
            action  = 'store',
            type    = bool,
            default = True,
            help    = "The format to convert to.",
        )),
        ('--requirements', dict(
            nargs='+',
            help=("Explicit requirements to add to the converted file.")
        )),

    )

    _targets = ('pyscript', 'pyodide')

    def invoke(self, args: argparse.Namespace) -> None:
        runtime = args.to
        if runtime not in self._targets:
            raise ValueError(f'Supported conversion targets include: {self._targets!r}') 

        requirements = args.requirements or 'auto'
        for f in args.files:
            html = script_to_html(
                f, requirements=requirements, runtime=runtime, prerender=args.prerender
            )
            filename = os.path.basename(f).split('.')[0]+'.html'
            with open(filename, 'w') as out:
                out.write(html)
            print(f'Successfully converted {f} to {runtime} target and wrote output to {filename}.') 
