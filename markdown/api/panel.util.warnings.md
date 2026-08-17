# panel.util.warnings module

exception panel.util.warnings.PanelDeprecationWarning
Bases: `DeprecationWarning`

A Panel-specific `DeprecationWarning` subclass.
Used to selectively filter Panel deprecations for unconditional display.

exception panel.util.warnings.PanelUserWarning
Bases: `UserWarning`

A Panel-specific `UserWarning` subclass. Used
to selectively filter Panel warnings for unconditional display.

panel.util.warnings.find_stack_level() → int
Find the first place in the stack that is not inside Panel and Param.
Inspired by: pandas.util.\_exceptions.find_stack_level

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
