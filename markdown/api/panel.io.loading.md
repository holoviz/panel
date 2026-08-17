# panel.io.loading module

This module contains functionality to make any Panel component look like
it is loading and disabled.

panel.io.loading.start_loading_spinner(\*objects)
Changes the appearance of the specified panel objects to indicate that
they are loading.

This is done by

- adding a small spinner on top

- graying out the panel

- disabling the panel

- and changing the mouse cursor to a spinner when hovering over the
  panel

Parameters:
**objects: tuple**
The panels to add the loading indicator to.

panel.io.loading.stop_loading_spinner(\*objects)
Removes the loading indicating from the specified panel objects.

Parameters:
**objects: tuple**
The panels to remove the loading indicator from.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
