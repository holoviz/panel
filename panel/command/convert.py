import argparse
import os

from bokeh.command.subcommand import Argument, Subcommand

from ..io.convert import script_to_html, make_index


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
        ('--out', dict(
            action  = 'store',
            type    = str,
            help    = "The directory to write the file to.",
        )),
        ('--prerender', dict(
            action  = 'store',
            type    = bool,
            default = True,
            help    = "The format to convert to.",
        )),
        ('--index', dict(
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

        if args.out:
            os.makedirs(args.out, exist_ok=True)
        requirements = args.requirements or 'auto'
        files = []
        for f in args.files:
            try:
                html = script_to_html(
                    f, requirements=requirements, runtime=runtime, prerender=args.prerender
                )
            except:
                print(f'Failed toconvert {f} to {runtime} target.')
                continue
            filename = os.path.basename(f).split('.')[0]+'.html'
            files.append(filename)
            if args.out:
                filename = os.path.join(args.out, filename)
            with open(filename, 'w') as out:
                out.write(html)
            print(f'Successfully converted {f} to {runtime} target and wrote output to {filename}.')
        if args.index:
            index = make_index(files)
            index_file = os.path.join(args.out, 'index.html') if args.out else 'index.html'
            with open(index_file, 'w') as f:
                f.write(index)
