"""Config for building Panel markdown docs and llms.txt."""

from __future__ import annotations

from pathlib import Path

from nbsite.scripts import LlmsBuildConfig, LlmsSection, MarkdownSource

ROOT = Path(__file__).parent.parent
DOC_DIR = ROOT / "doc"
BUILTDOCS_DIR = ROOT / "builtdocs"
OUTPUT_DIR = BUILTDOCS_DIR / "markdown"

_MD_PAGE = lambda p: p.suffix == ".md" and p.stem != "index"

# Files that carry no LLM code-gen value and should be excluded from the build.
EXCLUDE_FILES = (
    Path("releases.md"),
    Path("roadmap.md"),
    Path("about.md"),
    Path("community.md"),
)


def _label(path: Path) -> str:
    if path.stem == "index":
        return "home" if path.parent == Path(".") else path.parent.name.replace("_", " ")
    return path.stem.removeprefix("panel.").replace(".", " ").replace("_", " ")


CONFIG = LlmsBuildConfig(
    project_title="Panel",
    project_description=(
        "Panel is a Python library for building powerful interactive dashboards, apps, "
        "and data tools entirely in Python.\n"
        "This file lists the most important documentation pages for LLM-assisted "
        "development; not all generated doc links are shown."
    ),
    markdown_root=OUTPUT_DIR,
    llms_output_path=BUILTDOCS_DIR / "llms.txt",
    markdown_base_url="/markdown",
    sources=(
        MarkdownSource(
            source_dir=DOC_DIR,
            output_dir=OUTPUT_DIR,
            rendered_source_dir=BUILTDOCS_DIR,
            exclude_dir_names=("about", ".ipynb_checkpoints", "developer_guide"),
            exclude_files=EXCLUDE_FILES,
        ),
    ),
    sections=(
        LlmsSection(
            title="getting started",
            description="Install Panel and learn the core concepts.",
            path_prefix=Path("getting_started"),
            path_filter=_MD_PAGE,
            label_builder=_label,
            group="Documentation",
        ),
        LlmsSection(
            title="tutorials",
            description="Basic, intermediate, and expert learning paths.",
            path_prefix=Path("tutorials"),
            path_filter=_MD_PAGE,
            url_pattern="/markdown/tutorials/{path}.md",
            group="Documentation",
        ),
        LlmsSection(
            title="how-to",
            description="Practical recipes for common Panel tasks.",
            path_prefix=Path("how_to"),
            path_filter=_MD_PAGE,
            url_pattern="/markdown/how_to/{path}.md",
            group="Documentation",
        ),
        LlmsSection(
            title="concepts",
            description="Background on APIs, dependencies, and components.",
            path_prefix=Path("explanation"),
            path_filter=_MD_PAGE,
            url_pattern="/markdown/explanation/{path}.md",
            group="Documentation",
        ),
        LlmsSection(
            title="gallery",
            description="Representative example applications.",
            path_prefix=Path("gallery"),
            path_filter=_MD_PAGE,
            url_pattern="/markdown/gallery/{stem}.md",
            group="Documentation",
        ),
        LlmsSection(
            title="reference",
            description=(
                "Detailed reference galleries for every pane, widget, layout, template, "
                "and other component.\n Each page documents construction and usage, all "
                "available parameters, and how to customize appearance and behavior."
            ),
            path_prefix=Path("reference"),
            path_filter=_MD_PAGE,
            url_pattern="/markdown/reference/{path}.md",
            group="Documentation",
        ),
        LlmsSection(
            title="API Reference",
            description="Key API module reference pages.",
            path_prefix=Path("api"),
            path_filter=_MD_PAGE,
            url_pattern="/markdown/api/{stem}.md",
        ),
    ),
)
