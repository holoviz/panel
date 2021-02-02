"""
Commandline interface to Panel
"""
import sys
import argparse

from bokeh.__main__ import main as bokeh_entry_point
from bokeh.command.subcommands.serve import Serve as BkServe
from bokeh.command.util import die
from bokeh.util.string import nice_join

from .. import __version__
from .serve import Serve
from .oauth_secret import OAuthSecret


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
    """Merges commands offered by pyct and bokeh and provides help for both"""
    from bokeh.command.subcommands import all as bokeh_commands
    bokeh_commands = bokeh_commands + [OAuthSecret]

    try:
        import pyct.cmd
        pyct_commands = ['copy-examples', 'examples']
    except Exception:
        pass

    parser = argparse.ArgumentParser(
        prog="panel", epilog="See '<command> --help' to read about a specific subcommand."
    )

    parser.add_argument('-v', '--version', action='version', version=__version__)

    subs = parser.add_subparsers(help="Sub-commands")

    for cmd in pyct_commands:
        cmd = cmd.replace('-', '_')
        fn = getattr(pyct.cmd, cmd)
        subs.add_parser(cmd, help=fn.__doc__)

    for cls in bokeh_commands:
        if cls is BkServe:
            subparser = subs.add_parser(Serve.name, help=Serve.help)
            subcommand = Serve(parser=subparser)
            subparser.set_defaults(invoke=subcommand.invoke)
        else:
            subs.add_parser(cls.name, help=cls.help)

    if len(sys.argv) == 1:
        all_commands = sorted([c.name for c in bokeh_commands] + pyct_commands)
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
        else:
            ret = bokeh_entry_point()
    elif sys.argv[1] in pyct_commands:
        try:
            import pyct.cmd
        except ImportError:
            print("install pyct to enable this command (e.g. `conda install -c pyviz pyct` or `pip install pyct[cmd]`)")
            sys.exit(1)
        pyct.cmd.substitute_main('panel', cmds=pyct_commands, args=args)
    else:
        parser.parse_args(sys.argv[1:])
        sys.exit(1)

    if ret is False:
        sys.exit(1)
    elif ret is not True and isinstance(ret, int) and ret != 0:
        sys.exit(ret)



if __name__ == "__main__":
    main()
