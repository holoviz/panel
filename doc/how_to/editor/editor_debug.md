# Debug Apps in an Editor

This guide addresses how to debug apps in your favorite IDE or editor.

---

The simplest way to debug is to insert a `breakpoint()` in your code and then serve your app from a terminal. Type `help` in the debugger to see the available *commands*.

<img src="../../_static/terminal-breakpoint.png" styles="max-height:300px;max-width:100%"></img>

If your editor or IDE provides *integrated debugging* you can also use that in one of two ways.

- Use `.servable()` and configure your editor to start debugging using the command `python -m panel serve <name-of-script.py>`. This is our recommended method.
- Use `.show()` on a single Panel component. This is an alternative method.

For more details check out the [VS Code Debug Configuration Guide](vscode_configure#debugging).
