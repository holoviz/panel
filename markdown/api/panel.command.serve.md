# panel.command.serve module

Subclasses the bokeh serve commandline handler to extend it in various
ways.

class panel.command.serve.AdminApplicationContext(application, unused_timeout=15000, **kwargs)
Bases: `ApplicationContext`

Methods

|                      |     |
|----------------------|-----|
| **cleanup_sessions** |     |
| **run_load_hook**    |     |
| **run_unload_hook**  |     |

class panel.command.serve.Serve(parser: ArgumentParser)
Bases: `Serve`

Methods

|  |  |
|----|----|
| [customize_applications](#panel.command.serve.Serve.customize_applications)(args, applications) | Allows subclasses to customize `applications`. |
| [customize_kwargs](#panel.command.serve.Serve.customize_kwargs)(args, server_kwargs) | Allows subclasses to customize `server_kwargs`. |

|                       |     |
|-----------------------|-----|
| **invoke**            |     |
| **warm_applications** |     |

customize_applications(args, applications)
Allows subclasses to customize `applications`.

Should modify and return a copy of the
`applications` dictionary.

customize_kwargs(args, server_kwargs)
Allows subclasses to customize `server_kwargs`.

Should modify and return a copy of the
`server_kwargs` dictionary.

invoke(args: argparse.Namespace)

panel.command.serve.add_sys_path(path: str \| os.PathLike) → Iterator\[None\]
Temporarily add the given path to sys.path.

panel.command.serve.parse_var(s)
Parse a key, value pair, separated by ‘=’ That’s the reverse of
ShellArgs.

On the command line (argparse) a declaration will typically look like:
foo=hello

or
foo=”hello world”

panel.command.serve.parse_vars(items)
Parse a series of key-value pairs and return a dictionary

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
