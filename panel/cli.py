"""
Commandline interface to Panel
"""

import sys
from bokeh.__main__ import main as bokeh_entry_point


def transform_cmds(argv):
    """
    Updates the argv list to remap anaconda-project arguments appropriately.
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


def main():
    sys.argv = transform_cmds(sys.argv)
    bokeh_entry_point()
