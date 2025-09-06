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
from ..config import config
from .bundle import Bundle
from .compile import Compile
from .convert import Convert
from .oauth_secret import OAuthSecret
from .serve import Serve

_DESCRIPTION = """\
Found a Bug or Have a Feature Request?
Open an issue at: https://github.com/holoviz/panel/issues

Have a Question?
Ask on our Discord chat server: https://discord.gg/rb6gPXbdAr

Need Help?
Ask a question on our forum: https://discourse.holoviz.org

For more information, see the documentation at: https://panel.holoviz.org """


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


def main(args: list[str] | None = None):
    from bokeh.command.subcommands import all as bokeh_commands
    parser = argparse.ArgumentParser(
        prog="panel", epilog="See '<command> --help' to read about a specific subcommand.",
        description=_DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-v', '--version', action='version', version=__version__)
    subs = parser.add_subparsers(help="Sub-commands")

    commands = list(bokeh_commands)
    for command in commands:
        if command is not BkServe:
            subs.add_parser(command.name, help=command.help)
    for extra in (Bundle, Compile, Convert, OAuthSecret, Serve):
        commands.append(extra)
        subparser = subs.add_parser(extra.name, help=extra.help)
        subcommand = extra(parser=subparser)
        subparser.set_defaults(invoke=subcommand.invoke)

    if len(sys.argv) == 1:
        all_commands = sorted([c.name for c in commands])
        die(f"ERROR: Must specify subcommand, one of: {nice_join(all_commands)}")
    elif len(sys.argv) > 1 and any(sys.argv[1] == c.name for c in commands):
        sys.argv = transform_cmds(sys.argv)
        if sys.argv[1] in ('bundle', 'compile', 'convert', 'serve', 'oauth-secret', 'help'):
            parsed_args = parser.parse_args(sys.argv[1:])
            try:
                ret = parsed_args.invoke(parsed_args)
            except Exception as e:
                if config.autoreload or config.log_level in ("DEBUG", "INFO"):
                    raise e
                die("ERROR: " + str(e))
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
