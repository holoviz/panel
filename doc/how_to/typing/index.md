# Type Checking with Param and Panel

This guide covers how to configure static type checkers (like mypy) when working with Panel and Param.

## Why this matters

Panel is built on top of [Param](https://param.holoviz.org), which uses a custom metaclass to route class-level parameter assignment through Python's descriptor protocol. Static type checkers like mypy don't understand this pattern out of the box, and will reject valid code such as:

```python
import panel as pn

pn.chat.ChatMessage.show_reaction_icons = False
```

Running mypy on this without the plugin produces an error:

```console
$ mypy script.py
script.py:3: error: Incompatible types in assignment (expression has type "bool", variable has type "Boolean[bool]")  [assignment]
Found 1 error in 1 file (checked 1 source file)
```

This is a real issue for projects that run mypy in CI/CD, since it can block releases or force you to spend time silencing false-positive errors.

To fix this, Param ships a dedicated mypy plugin.

## Enabling the Param mypy plugin

Add the following to your `pyproject.toml`:

```toml
[tool.mypy]
plugins = ["param.mypy_plugin"]
```

Or, if you're using `mypy.ini` / `setup.cfg`:

```ini
[mypy]
plugins = param.mypy_plugin
```

With the plugin enabled, mypy correctly understands that assignments like `pn.chat.ChatMessage.show_reaction_icons = False` set the parameter's default value, and type-checks them accordingly — no more false-positive errors in CI.

## Learn more

Param's user guide has a full [Typing guide](https://param.holoviz.org/en/latest/user_guide/Typing.html) covering:

- Type inference from Parameter types
- Choice of type checker (mypy, basedpyright)
- Known limitations
- Practical recommendations

If you're setting up type checking for a Panel project, that guide is the best place to go for details beyond the mypy plugin itself.