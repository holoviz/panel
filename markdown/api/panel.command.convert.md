# panel.command.convert module

class panel.command.convert.Convert(parser: ArgumentParser)
Bases: `Subcommand`

Subcommand to convert Panel application to some build target, e.g.
pyodide or pyscript.

Methods

|  |  |
|----|----|
| [invoke](#panel.command.convert.Convert.invoke)(args) | Takes over main program flow to perform the subcommand. |

invoke(args: Namespace) → None
Takes over main program flow to perform the subcommand.

*This method must be implemented by subclasses.* subclassed overwritten
methods return different types: bool: Build None: FileOutput (subclassed
by HTML, SVG and JSON. PNG overwrites FileOutput.invoke method), Info,
Init, Sampledata, Secret, Serve, Static

Args:
args (argparse.Namespace) : command line arguments for the subcommand to
parse

Raises:
NotImplementedError

name: ClassVar\[str\] = 'convert'
name for this subcommand

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
