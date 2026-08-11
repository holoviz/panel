"""Config for building Panel markdown docs and llms.txt."""

from __future__ import annotations

from pathlib import Path

from nbsite.scripts import LlmsBuildConfig, LlmsSection, MarkdownSource

ROOT = Path(__file__).parent.parent
DOC_DIR = ROOT / "doc"
BUILTDOCS_DIR = ROOT / "builtdocs"
MARKDOWN_DIR = BUILTDOCS_DIR / "markdown"
MARKDOWN_BASE_URL = "/markdown"

PAGES = {
    Path("index.md"),
    Path("FAQ.md"),
    Path("community.md"),
    Path("upgrade.md"),
    Path("getting_started/index.md"),
    Path("getting_started/build_app.md"),
    Path("getting_started/core_concepts.md"),
    Path("getting_started/installation.md"),
    Path("tutorials/index.md"),
    Path("tutorials/basic/index.md"),
    Path("tutorials/intermediate/index.md"),
    Path("tutorials/expert/index.md"),
    Path("how_to/index.md"),
    Path("how_to/components/index.md"),
    Path("how_to/layout/index.md"),
    Path("how_to/styling/index.md"),
    Path("how_to/interactivity/index.md"),
    Path("how_to/templates/index.md"),
    Path("how_to/custom_components/index.md"),
    Path("how_to/state/index.md"),
    Path("explanation/index.md"),
    Path("explanation/api/index.md"),
    Path("explanation/apis.md"),
    Path("explanation/components.md"),
    Path("explanation/dependencies.md"),
    Path("explanation/develop_seamlessly.md"),
    Path("gallery/index.md"),
    Path("gallery/portfolio_analyzer.md"),
    Path("gallery/webllm.md"),
    Path("reference/index.md"),
    Path("reference/chat/index.md"),
    Path("reference/indicators/index.md"),
    Path("reference/layouts/index.md"),
    Path("reference/panes/index.md"),
    Path("reference/templates/index.md"),
    Path("reference/widgets/index.md"),
    Path("api/index.md"),
    Path("api/panel.chat.md"),
    Path("api/panel.io.md"),
    Path("api/panel.layout.md"),
    Path("api/panel.pane.md"),
    Path("api/panel.template.md"),
    Path("about/index.md"),
    Path("about/releases.md"),
}

ROOT_PAGES = {
    Path("index.md"),
    Path("FAQ.md"),
    Path("community.md"),
    Path("upgrade.md"),
}


def _label(path: Path) -> str:
    if path.stem == "index":
        return "home" if path.parent == Path(".") else path.parent.name.replace("_", " ")
    return path.stem.removeprefix("panel.").replace(".", " ").replace("_", " ")


CONFIG = LlmsBuildConfig(
    project_title="Panel",
    project_description=(
        "Panel is a Python library for building powerful interactive dashboards, apps, "
        "and data tools entirely in Python. This file exposes the Panel docs as markdown "
        "for LLM-friendly browsing."
    ),
    markdown_root=MARKDOWN_DIR,
    llms_output_path=BUILTDOCS_DIR / "llms.txt",
    markdown_base_url=MARKDOWN_BASE_URL,
    sources=(
        MarkdownSource(
            source_dir=DOC_DIR,
            output_dir=MARKDOWN_DIR,
            rendered_source_dir=BUILTDOCS_DIR,
        ),
    ),
    sections=(
        LlmsSection(
            title="Home",
            description="Top-level pages and project overview.",
            path_prefix=Path("."),
            path_filter=lambda path: path in ROOT_PAGES,
            label_builder=_label,
        ),
        LlmsSection(
            title="Getting Started",
            description="Install Panel and learn the core concepts.",
            path_prefix=Path("getting_started"),
            path_filter=lambda path: path in PAGES,
            label_builder=_label,
        ),
        LlmsSection(
            title="Tutorials",
            description="Basic, intermediate, and expert learning paths.",
            path_prefix=Path("tutorials"),
            path_filter=lambda path: path in PAGES,
            label_builder=_label,
        ),
        LlmsSection(
            title="How-to",
            description="Practical recipes for common Panel tasks.",
            path_prefix=Path("how_to"),
            path_filter=lambda path: path in PAGES,
            label_builder=_label,
        ),
        LlmsSection(
            title="Concepts",
            description="Background on APIs, dependencies, and components.",
            path_prefix=Path("explanation"),
            path_filter=lambda path: path in PAGES,
            label_builder=_label,
        ),
        LlmsSection(
            title="Gallery",
            description="Representative example applications.",
            path_prefix=Path("gallery"),
            path_filter=lambda path: path in PAGES,
            label_builder=_label,
        ),
        LlmsSection(
            title="Reference",
            description="Component gallery landing pages.",
            path_prefix=Path("reference"),
            path_filter=lambda path: path in PAGES,
            label_builder=_label,
        ),
        LlmsSection(
            title="API Reference",
            description="Key API module reference pages.",
            path_prefix=Path("api"),
            path_filter=lambda path: path in PAGES,
            label_builder=_label,
        ),
        LlmsSection(
            title="About",
            description="Project background and roadmap pages.",
            path_prefix=Path("about"),
            path_filter=lambda path: path in PAGES,
            label_builder=_label,
        ),
    ),
)
