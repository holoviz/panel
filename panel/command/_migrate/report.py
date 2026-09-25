"""
Plain-text reporting for ``panel migrate``.

Kept separate from :mod:`.codemod` so both are independently testable: the
codemod produces the raw :class:`Rewrite`/:class:`ManualReview` records, this
module only knows how to format them.
"""
from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=True)
class Rewrite:
    """One applied rewrite."""

    line: int
    rule: str
    message: str


@dataclasses.dataclass(frozen=True)
class ManualReview:
    """One thing the codemod deliberately left alone."""

    line: int
    message: str


@dataclasses.dataclass
class FileResult:
    """The migration outcome for a single file."""

    path: str
    changed: bool
    rewrites: list[Rewrite] = dataclasses.field(default_factory=list)
    manual_reviews: list[ManualReview] = dataclasses.field(default_factory=list)
    parse_error: str | None = None


class Report:
    """
    Collects the per-file results of a ``panel migrate`` run and renders them
    as a human-readable text report.
    """

    def __init__(self) -> None:
        self.files: list[FileResult] = []

    def add(
        self,
        path: str,
        changed: bool,
        rewrites: list[Rewrite],
        manual_reviews: list[ManualReview],
        parse_error: str | None = None,
    ) -> None:
        self.files.append(FileResult(
            path=path, changed=changed, rewrites=list(rewrites), manual_reviews=list(manual_reviews),
            parse_error=parse_error,
        ))

    def render(self) -> str:
        lines: list[str] = []
        for file in self.files:
            if file.parse_error or not (file.rewrites or file.manual_reviews):
                continue
            lines.append(file.path)
            for rewrite in sorted(file.rewrites, key=lambda r: r.line):
                lines.append(f'  L{rewrite.line}: [{rewrite.rule}] {rewrite.message}')
            for review in sorted(file.manual_reviews, key=lambda r: r.line):
                lines.append(f'  L{review.line}: [manual review] {review.message}')
            lines.append('')

        parse_error_files = [f for f in self.files if f.parse_error]
        if parse_error_files:
            lines.append('Files that could not be parsed:')
            for file in parse_error_files:
                lines.append(f'  {file.path}: {file.parse_error}')
            lines.append('')

        lines.append(self.summary())
        return '\n'.join(lines).rstrip() + '\n'

    def summary(self) -> str:
        files_scanned = len(self.files)
        files_changed = sum(1 for f in self.files if f.changed and not f.parse_error)
        parse_errors = sum(1 for f in self.files if f.parse_error)
        rule_counts: dict[str, int] = {}
        manual_count = 0
        for file in self.files:
            if file.parse_error:
                continue
            for rewrite in file.rewrites:
                rule_counts[rewrite.rule] = rule_counts.get(rewrite.rule, 0) + 1
            manual_count += len(file.manual_reviews)
        if rule_counts:
            rule_summary = ', '.join(f'{count} {rule}' for rule, count in sorted(rule_counts.items()))
        else:
            rule_summary = 'none'
        parse_error_summary = f', {parse_errors} could not be parsed' if parse_errors else ''
        return (
            f'Summary: {files_scanned} file(s) scanned, {files_changed} changed{parse_error_summary}, '
            f'rewrites: {rule_summary}, manual review items: {manual_count}.'
        )
