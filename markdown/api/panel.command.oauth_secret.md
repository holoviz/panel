# panel.command.oauth_secret module

class panel.command.oauth_secret.OAuthSecret(parser: ArgumentParser)
Bases: `Subcommand`

Subcommand to generate a new encryption key.

Methods

|  |  |
|----|----|
| [invoke](#panel.command.oauth_secret.OAuthSecret.invoke)(args) | Takes over main program flow to perform the subcommand. |

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

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
