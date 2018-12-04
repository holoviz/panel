"""
Commandline interface to Panel
"""

import sys
from bokeh.__main__ import main as bokeh_entry_point


def transform_cmds(argv):
    """
    Allows usage with anaconda-project by remapping the argv list provided
    into arguments accepted by Bokeh 0.12.7 or later.
    """
    replacements = {'--anaconda-project-host':'--allow-websocket-origin',
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
    """Special case: Allow Bokeh to handle the `serve` command; rest is handled by pyct."""
    if len(sys.argv) > 1 and 'serve' == sys.argv[1]:
        sys.argv = transform_cmds(sys.argv)
        bokeh_entry_point()
    else:
        try:
            import pyct.cmd
        except ImportError:
            print("install pyct to enable this command (e.g. `conda install -c pyviz pyct` or `pip install pyct[cmd]`)")
            sys.exit(1)
        pyct.cmd.substitute_main('panel',args=args)

if __name__ == "__main__":
    main()
