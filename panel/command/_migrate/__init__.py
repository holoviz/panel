"""
Implementation package for the ``panel migrate`` subcommand
(:mod:`panel.command.migrate`).

Not part of the public API. Split into:

- :mod:`.compat` -- introspects the installed ``panel``/``panel.ui``
  namespaces to build the lookup data the codemod needs. Has no dependency on
  ``libcst`` so it can be imported without the optional ``migrate`` extra.
- :mod:`.codemod` -- the ``libcst`` transform implementing the rewrite rules.
- :mod:`.report` -- plain-text report formatting.
"""
