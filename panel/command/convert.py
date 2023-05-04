import argparse
import json
import pathlib
import time

from bokeh.command.subcommand import Argument, Subcommand

from ..io.convert import convert_apps


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
            help    = "The format to convert to, one of 'pyodide' (default), 'pyodide-worker' or 'pyscript'",
            default = 'pyodide'
        )),
        ('--out', dict(
            action  = 'store',
            type    = str,
            help    = "The directory to write the file to.",
        )),
        ('--title', dict(
            action  = 'store',
            type    = str,
            help    = "A custom title for the application(s).",
        )),
        ('--skip-embed', dict(
            action  = 'store_true',
            help    = "Whether to skip embedding pre-rendered content in the converted file to display content while app is loading.",
        )),
        ('--index', dict(
            action  = 'store_true',
            help    = "Whether to create an index if multiple files are served.",
        )),
        ('--pwa', dict(
            action  = 'store_true',
            help    = "Whether to add files to serve applications as a Progressive Web App.",
        )),
        ('--requirements', dict(
            nargs   = '+',
            help    = (
                "Explicit requirements to add to the converted file, a single requirements.txt file or a "
                "JSON file containing requirements per app. By default requirements are inferred from the code."
            )
        )),
        ('--disable-http-patch', dict(
            default = False,
            action  = 'store_false',
            help    = "Whether to disable patching http requests using the pyodide-http library."
        )),
        ('--watch', dict(
            action  = 'store_true',
            help    = "Watch the files"
        )),
        ('--num-procs', dict(
            action  = 'store',
            type    = int,
            default = 1,
            help    = "The number of processes to start in parallel to convert the apps."
        )),
    )

    _targets = ('pyscript', 'pyodide', 'pyodide-worker')

    def invoke(self, args: argparse.Namespace) -> None:
        runtime = args.to.lower()
        if runtime not in self._targets:
            raise ValueError(f'Supported conversion targets include: {self._targets!r}')
        requirements = args.requirements or 'auto'
        if (
            isinstance(requirements, list) and
            len(requirements) == 1 and
            pathlib.Path(requirements[0]).is_file()
        ):
            req = requirements[0]
            if req.endswith('.txt'):
                requirements = requirements[0]
            elif req.endswith('.json'):
                with open(req, encoding='utf-8') as req_file:
                    requirements = json.load(req_file)
        prev_hashes = {}
        built = False
        while True:
            hashes = {f: hash(open(f).read()) for f in args.files}
            if hashes == prev_hashes:
                time.sleep(0.5)
                continue
            files = [f for f, h in hashes.items() if prev_hashes.get(f) != h]
            index = args.index and not built
            try:
                convert_apps(
                    files, dest_path=args.out, runtime=runtime, requirements=requirements,
                    prerender=not args.skip_embed, build_index=index, build_pwa=args.pwa,
                    title=args.title, max_workers=args.num_procs,
                    http_patch=not args.disable_http_patch, verbose=True
                )
            except KeyboardInterrupt:
                print("Aborted while building docs.")
                break
            built = True
            prev_hashes = hashes
            if not args.watch:
                return
