# panel.command.compile module

class panel.command.compile.Compile(parser: ArgumentParser)
Bases: `Subcommand`

Subcommand to generate a new encryption key.

Methods

|  |  |
|----|----|
| [invoke](#panel.command.compile.Compile.invoke)(args) | Takes over main program flow to perform the subcommand. |

invoke(args)
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

name: ClassVar\[str\] = 'compile'
name for this subcommand

panel.command.compile.run_compile(bundles: dict\[pathlib.Path, list\[type\[ReactiveESM\]\]\], build_dir: str \| os.PathLike \| None = None, unminified: bool = False, skip_npm: bool = False, file_loaders: list\[str\] \| None = None, verbose: bool = False) → int
Runs the compile command on the provided bundles.

Parameters:
bundles : dict\[type\[ReactiveESM\]\]
A list of ReactiveESM component classes to compile.

build_dir : str \| os.PathLike, optional
The directory where the build output will be saved. If None, a temporary
directory will be used.

unminified : bool, optional
If True, minifies the compiled JavaScript bundle.

**skip_npm: bool**
Whether to skip npm install (assumes build_dir is set)

**file_loaders: list\[str\]**
List of file types (e.g. woff2 or svg) loaders to carry along

verbose : bool, optional
If True, prints detailed logs during the compilation process.

Returns:
int:
Count of errors.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
