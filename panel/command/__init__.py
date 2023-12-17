"""
Commandline interface to Panel
"""
import argparse
import os
import sys

from bokeh.__main__ import main as bokeh_entry_point
from bokeh.command.subcommands.serve import Serve as BkServe
from bokeh.command.util import die
from bokeh.util.strings import nice_join

from .. import __version__
from .bundle import Bundle
from .convert import Convert
from .oauth_secret import OAuthSecret
from .serve import Serve


def transform_cmds(argv):
    """
    Allows usage with anaconda-project by remapping the argv list provided
    into arguments accepted by Bokeh 0.12.7 or later.
    """
    replacements = {
        '--anaconda-project-host':'--allow-websocket-origin',
        '--anaconda-project-port': '--port',
        '--anaconda-project-address': '--address'
    }
    if 'PANEL_AE5_CDN' in os.environ:
        # Override AE5 default
        os.environ['BOKEH_RESOURCES'] = 'cdn'
    transformed = []
    skip = False
    for arg in argv:
        if skip:
            skip = False
            continue
        if arg in replacements.keys():
            transformed.append(replacements[arg])
        elif arg == '--anaconda-project-iframe-hosts':
            skip = True
            continue
        elif arg.startswith('--anaconda-project'):
            continue
        else:
            transformed.append(arg)
    return transformed


def main(args=None):
    """Mirrors bokeh CLI and adds additional Panel specific commands """
    from bokeh.command.subcommands import all as bokeh_commands
    bokeh_commands = bokeh_commands + [OAuthSecret, Convert, Bundle]

    parser = argparse.ArgumentParser(
        prog="panel", epilog="See '<command> --help' to read about a specific subcommand."
    )

    parser.add_argument('-v', '--version', action='version', version=__version__)

    subs = parser.add_subparsers(help="Sub-commands")

    for cls in bokeh_commands:
        if cls is BkServe:
            subparser = subs.add_parser(Serve.name, help=Serve.help)
            subcommand = Serve(parser=subparser)
            subparser.set_defaults(invoke=subcommand.invoke)
        elif cls is Convert:
            subparser = subs.add_parser(Convert.name, help=Convert.help)
            subcommand = Convert(parser=subparser)
            subparser.set_defaults(invoke=subcommand.invoke)
        elif cls is Bundle:
            subparser = subs.add_parser(Bundle.name, help=Bundle.help)
            subcommand = Bundle(parser=subparser)
            subparser.set_defaults(invoke=subcommand.invoke)
        else:
            subs.add_parser(cls.name, help=cls.help)

    if len(sys.argv) == 1:
        all_commands = sorted([c.name for c in bokeh_commands])
        die("ERROR: Must specify subcommand, one of: %s" % nice_join(all_commands))

    if sys.argv[1] in ('--help', '-h'):
        args = parser.parse_args(sys.argv[1:])
        args.invoke(args)
        sys.exit()

    if len(sys.argv) > 1 and any(sys.argv[1] == c.name for c in bokeh_commands):
        sys.argv = transform_cmds(sys.argv)
        if sys.argv[1] == 'serve':
            args = parser.parse_args(sys.argv[1:])
            try:
                ret = args.invoke(args)
            except Exception as e:
                die("ERROR: " + str(e))
        elif sys.argv[1] == 'oauth-secret':
            ret = OAuthSecret(parser).invoke(args)
        elif sys.argv[1] == 'convert':
            args = parser.parse_args(sys.argv[1:])
            ret = Convert(parser).invoke(args)
        elif sys.argv[1] == 'bundle':
            args = parser.parse_args(sys.argv[1:])
            ret = Bundle(parser).invoke(args)
        else:
            ret = bokeh_entry_point()
    else:
        parser.parse_args(sys.argv[1:])
        sys.exit(1)

    if ret is False:
        sys.exit(1)
    elif ret is not True and isinstance(ret, int) and ret != 0:
        sys.exit(ret)



if __name__ == "__main__":
    main()
