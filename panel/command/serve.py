"""
Subclasses the bokeh serve commandline handler to extend it in various
ways.
"""

from bokeh.command.subcommands.serve import Serve as _BkServe

from ..io.server import INDEX_HTML, get_static_routes

def parse_var(s):
    """
    Parse a key, value pair, separated by '='
    That's the reverse of ShellArgs.

    On the command line (argparse) a declaration will typically look like:
        foo=hello
    or
        foo="hello world"
    """
    items = s.split('=')
    key = items[0].strip() # we remove blanks around keys, as is logical
    if len(items) > 1:
        # rejoin the rest:
        value = '='.join(items[1:])
    return (key, value)


def parse_vars(items):
    """
    Parse a series of key-value pairs and return a dictionary
    """
    return dict((parse_var(item) for item in items))


class Serve(_BkServe):

    args = _BkServe.args + (
        ('--static-dirs', dict(
            metavar="KEY=VALUE",
            nargs='+',
            help=("Static directories to serve specified as key=value "
                  "pairs mapping from URL route to static file directory.")
        )),
    )
    
    def customize_kwargs(self, args, server_kwargs):
        '''Allows subclasses to customize ``server_kwargs``.

        Should modify and return a copy of the ``server_kwargs`` dictionary.
        '''
        kwargs = dict(server_kwargs)
        if 'index' not in kwargs:
            kwargs['index'] = INDEX_HTML

        # Handle tranquilized functions in the supplied functions
        kwargs['extra_patterns'] = patterns = []

        if args.static_dirs:
            patterns += get_static_routes(parse_vars(args.static_dirs))

        return kwargs
