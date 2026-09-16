"""
CLI subcommand rewriting classic Panel source code to the ``panel.ui``
namespace (plan §10.1).

The heavy lifting lives in :mod:`panel.command._migrate`, which is only
imported inside :meth:`Migrate.invoke`: ``libcst`` is an optional dependency
(``pip install panel[migrate]``), and importing it eagerly here would make it
a hard dependency of every ``panel`` command, including ones that have
nothing to do with migration.
"""
from __future__ import annotations

import difflib
import os
import pathlib
import sys
import typing as t

from bokeh.command.subcommand import Argument, Subcommand

if t.TYPE_CHECKING:
    import argparse

_INSTALL_MESSAGE = (
    "panel migrate requires libcst, which is not installed. "
    "Install it with `pip install panel[migrate]`."
)


def _iter_python_files(paths: list[str]) -> list[pathlib.Path]:
    """
    Expand a list of file and/or directory arguments into a sorted, deduped
    list of ``*.py`` files, walking directories recursively and skipping
    ``__pycache__``, hidden directories, and anything under ``.git``.
    """
    files: set[pathlib.Path] = set()
    for raw in paths:
        path = pathlib.Path(raw)
        if path.is_dir():
            for root, dirs, filenames in os.walk(path):
                root_path = pathlib.Path(root)
                if '.git' in root_path.parts:
                    dirs[:] = []
                    continue
                dirs[:] = [d for d in dirs if d != '__pycache__' and not d.startswith('.')]
                for filename in filenames:
                    if filename.endswith('.py'):
                        files.add(root_path / filename)
        elif path.is_file():
            files.add(path)
        else:
            print(f'{path} does not exist, skipping.')  # noqa
    return sorted(files)


class Migrate(Subcommand):
    """
    Subcommand rewriting classic Panel source code to the panel.ui namespace.
    """

    name = "migrate"

    help = "Rewrites classic Panel source code to use the panel.ui namespace"

    args = (
        ('paths', Argument(
            metavar = 'PATH',
            nargs   = '+',
            help    = "Files and/or directories to migrate; directories are walked recursively for *.py files.",
        )),
        ('--check', Argument(
            action  = 'store_true',
            help    = "Report which files would change without modifying them; exits non-zero if any file would change.",
        )),
        ('--diff', Argument(
            action  = 'store_true',
            help    = "Print a unified diff of the changes without modifying any file.",
        )),
    )

    def invoke(self, args: argparse.Namespace) -> int:
        try:
            import libcst  # noqa: F401
        except ImportError:
            print(_INSTALL_MESSAGE)  # noqa
            return 1

        from ._migrate.codemod import migrate_source
        from ._migrate.report import Report

        files = _iter_python_files(args.paths)
        if not files:
            print('No Python files found to migrate.')  # noqa
            return 0

        report = Report()
        any_changed = False
        any_parse_error = False
        for path in files:
            source = path.read_text(encoding='utf-8')
            result = migrate_source(source)
            report.add(
                str(path), result.changed, result.rewrites, result.manual_reviews, result.parse_error,
            )
            if result.parse_error is not None:
                any_parse_error = True
                continue
            if not result.changed:
                continue
            any_changed = True
            if args.diff:
                diff = difflib.unified_diff(
                    source.splitlines(keepends=True),
                    result.source.splitlines(keepends=True),
                    fromfile=str(path), tofile=str(path),
                )
                sys.stdout.writelines(diff)
            elif not args.check:
                path.write_text(result.source, encoding='utf-8')

        if not args.diff:
            print(report.render())  # noqa

        if any_parse_error:
            return 1
        if args.check:
            return 1 if any_changed else 0
        return 0
