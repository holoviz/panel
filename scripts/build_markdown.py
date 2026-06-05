"""
Build markdown output for docs and reference notebooks.

Copies all .md files from doc/ into builtdocs/markdown/ (stripping the doc/ prefix),
converts examples/reference notebooks to markdown using nbconvert, and generates
an llms.txt index at the documentation root.
"""

import shutil
import subprocess
import sys

from pathlib import Path

ROOT = Path(__file__).parent.parent
DOC_DIR = ROOT / "doc"
REFERENCE_DIR = ROOT / "examples" / "reference"
OUTPUT_DIR = ROOT / "builtdocs" / "markdown"
BUILTDOCS_DIR = ROOT / "builtdocs"

MARKDOWN_BASE_URL = "/markdown"

SECTION_DESCRIPTIONS = {
    "getting_started": "Installation and first steps with Panel",
    "tutorials/basic": "Beginner tutorials covering core concepts, layouts, widgets, and building simple apps",
    "tutorials/intermediate": "Intermediate tutorials on reusable components, testing, and server deployment",
    "tutorials/expert": "Advanced tutorials on custom ESM/JS/anywidget components",
    "how_to/authentication": "Configuring authentication, authorization, and OAuth providers",
    "how_to/caching": "Memoization and manual caching strategies",
    "how_to/callbacks": "Scheduling, async, periodic, and session lifecycle callbacks",
    "how_to/components": "Constructing panes, widgets, and managing layout children",
    "how_to/concurrency": "Threading, async, Dask, and load balancing for concurrent apps",
    "how_to/custom_components": "Building custom components with ESM, ReactiveHTML, or Python",
    "how_to/deployment": "Deploying Panel apps to cloud platforms (AWS, GCP, Azure, Hugging Face, etc.)",
    "how_to/export": "Saving and embedding Panel apps as static HTML or Bokeh documents",
    "how_to/interactivity": "Binding functions, generators, and reactive expressions to widgets",
    "how_to/layout": "Sizing, alignment, and spacing of components",
    "how_to/links": "JS callbacks, JS links, and bidirectional widget linking",
    "how_to/notebook": "Using Panel inside Jupyter notebooks and JupyterLab",
    "how_to/performance": "Throttling updates, holding events, and reusing sessions",
    "how_to/server": "Command-line serving, programmatic server, proxies, websockets, and endpoints",
    "how_to/styling": "CSS, design systems, theming, and styling plots (Altair, Plotly, Vega, etc.)",
    "how_to/templates": "Arranging components in page templates and creating custom templates",
    "how_to/test": "Unit testing, UI testing with Playwright, and load testing",
    "how_to/wasm": "Running Panel apps in the browser via Pyodide/WASM",
    "how_to/integrations": "Integrating Panel with Django, FastAPI, Flask, and Tornado",
    "how_to/streamlit_migration": "Migrating from Streamlit to Panel",
    "explanation": "Conceptual explanations of Panel architecture, APIs, and design decisions",
    "api": "API reference and cheatsheet",
    "developer_guide": "Contributing to Panel: development setup, docs, extensions",
}

REFERENCE_DESCRIPTIONS = {
    "chat": "Chat components (ChatFeed, ChatInterface, ChatMessage, etc.)",
    "custom_components": "Custom component base classes (JSComponent, ReactComponent, PyComponent, Viewer)",
    "global": "Global utilities (Notifications)",
    "indicators": "Indicator widgets (Gauge, Progress, Number, Trend, etc.)",
    "layouts": "Layout containers (Column, Row, Tabs, GridSpec, Card, Modal, etc.)",
    "panes": "Display panes for rendering content (Markdown, HTML, Plotly, Matplotlib, Bokeh, etc.)",
    "templates": "Page templates (Material, Bootstrap, FastList, Vanilla, etc.)",
    "widgets": "Interactive input widgets (Slider, Select, TextInput, Button, Tabulator, etc.)",
    "extensions": "Extension components",
}


def copy_markdown_docs():
    """Copy all .md files from doc/ preserving directory structure."""
    for md_file in DOC_DIR.rglob("*.md"):
        rel = md_file.relative_to(DOC_DIR)
        dest = OUTPUT_DIR / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(md_file, dest)
    print(f"Copied markdown docs to {OUTPUT_DIR}")


def convert_reference_notebooks():
    """Convert examples/reference notebooks to markdown using nbconvert."""
    ref_output = OUTPUT_DIR / "reference"
    notebooks = [
        nb for nb in REFERENCE_DIR.rglob("*.ipynb")
        if ".ipynb_checkpoints" not in str(nb)
    ]
    print(f"Converting {len(notebooks)} reference notebooks...")

    for nb in notebooks:
        rel = nb.relative_to(REFERENCE_DIR)
        dest_dir = ref_output / rel.parent
        dest_dir.mkdir(parents=True, exist_ok=True)

        result = subprocess.run(
            [
                sys.executable, "-m", "nbconvert",
                "--to", "markdown",
                "--output-dir", str(dest_dir),
                str(nb),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"  WARNING: failed to convert {rel}: {result.stderr.strip()}")
        else:
            print(f"  Converted {rel}")

    print(f"Reference notebooks written to {ref_output}")


def generate_llms_txt():
    """Generate llms.txt index file at the documentation root."""
    lines = []
    lines.append("# Panel")
    lines.append("")
    lines.append(
        "Panel is an open-source Python framework for building interactive web apps "
        "and dashboards from notebooks or scripts. It supports multiple plotting libraries, "
        "provides rich widgets, and can be deployed as standalone server apps or compiled to WASM."
    )
    lines.append("")
    lines.append(
        "All documentation is available as markdown files under the /markdown/ path. "
        "Reference docs for individual components are under /markdown/reference/."
    )
    lines.append("")

    # Documentation sections
    lines.append("## Documentation")
    lines.append("")
    for section, description in SECTION_DESCRIPTIONS.items():
        section_dir = OUTPUT_DIR / section
        if not section_dir.exists():
            continue
        md_files = sorted(section_dir.rglob("*.md"))
        md_files = [f for f in md_files if f.name != "index.md"]
        if not md_files:
            continue
        lines.append(f"### {section}")
        lines.append(f"> {description}")
        lines.append("")
        for md_file in md_files:
            rel = md_file.relative_to(OUTPUT_DIR)
            name = md_file.stem.replace("_", " ").title()
            lines.append(f"- [{name}]({MARKDOWN_BASE_URL}/{rel})")
        lines.append("")

    # Reference section
    lines.append("## Component Reference")
    lines.append("")
    lines.append(
        "Detailed reference documentation for every Panel component, "
        "converted from interactive notebooks."
    )
    lines.append("")
    ref_dir = OUTPUT_DIR / "reference"
    for category in sorted(ref_dir.iterdir()):
        if not category.is_dir() or category.name.startswith("."):
            continue
        description = REFERENCE_DESCRIPTIONS.get(category.name, "")
        lines.append(f"### {category.name}")
        if description:
            lines.append(f"> {description}")
        lines.append("")
        md_files = sorted(category.glob("*.md"))
        for md_file in md_files:
            rel = md_file.relative_to(OUTPUT_DIR)
            name = md_file.stem
            lines.append(f"- [{name}]({MARKDOWN_BASE_URL}/{rel})")
        lines.append("")

    llms_txt_path = BUILTDOCS_DIR / "llms.txt"
    llms_txt_path.write_text("\n".join(lines))
    print(f"Generated {llms_txt_path}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    copy_markdown_docs()
    convert_reference_notebooks()
    generate_llms_txt()


if __name__ == "__main__":
    main()
