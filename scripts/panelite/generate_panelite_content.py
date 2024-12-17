"""
Helper script to convert and copy example notebooks into JupyterLite build.
"""
import json
import os
import pathlib
import re
import shutil

from test.notebooks_with_panelite_issues import NOTEBOOK_ISSUES

import nbformat

HERE = pathlib.Path(__file__).parent
PANEL_BASE = HERE.parent.parent
EXAMPLES_DIR = PANEL_BASE / 'examples'
LITE_FILES = PANEL_BASE / 'lite' / 'files'
DOC_DIR = PANEL_BASE / 'doc'
BASE_DEPENDENCIES = []
MINIMUM_VERSIONS = {}

INLINE_DIRECTIVE = re.compile(r'\{.*\}`.*`\s*')

# Add piplite command to notebooks
with open(DOC_DIR / 'pyodide_dependencies.json', encoding='utf8') as file:
    DEPENDENCIES = json.load(file)

class DependencyNotFound(Exception):
    """Raised if a dependency cannot be found"""

def _notebook_key(nbpath: pathlib.Path):
    nbpath = str(nbpath).replace(os.path.sep, "/")
    return nbpath.replace(str(EXAMPLES_DIR), '').replace(str(DOC_DIR), '')[1:]

def _get_dependencies(nbpath: pathlib.Path):
    key = _notebook_key(nbpath)
    dependencies = DEPENDENCIES.get(key, [])
    if dependencies is None:
        return []
    for name, min_version in MINIMUM_VERSIONS.items():
        if any(name in req for req in dependencies):
            dependencies = [f'{name}>={min_version}' if name in req else req for req in dependencies]
    return BASE_DEPENDENCIES + dependencies

def _to_piplite_install_code(dependencies):
    dependencies = [repr(dep) for dep in dependencies]
    return f"import piplite\nawait piplite.install([{', '.join(dependencies)}])"

def _get_install_code_cell(dependencies):
    source = _to_piplite_install_code(dependencies)
    install = nbformat.v4.new_code_cell(source=source)
    del install['id']
    return install

def _get_issues(key):
    return NOTEBOOK_ISSUES.get(key, [])

def _to_issue_str(issue:str):
    if issue.startswith("https://github.com/") and "/issues/" in issue:
        issue = issue.replace("https://github.com/", "")
        _, library, _, id = issue.split("/")
        if library == "panel":
            return f"#{id}"
        return f"{library}#{id}"
    if issue.startswith("https://gitlab.kitware.com/") and "/issues/" in issue:
        issue = issue.replace("https://gitlab.kitware.com/", "")
        _, library, _, _, id = issue.split("/")
        if library == "panel":
            return f"#{id}"
        return f"{library}#{id}"
    return issue

def _get_info_markdown_cell(nbpath):
    key = _notebook_key(nbpath)
    issues = _get_issues(key)
    if issues:
        issues_str = ", ".join([f'<a href="{issue}">{_to_issue_str(issue)}</a>' for issue in issues])
        source = f"""<div class="alert alert-block alert-danger">
This notebook is not expected to run successfully in <em>Panelite</em>. It has the following known issues: {issues_str}.

Panelite is powered by young technologies like <a href="https://pyodide.org/en/stable/">Pyodide</a> and <a href="https://jupyterlite.readthedocs.io/en/latest/">Jupyterlite</a>. Some browsers may be poorly supported (e.g. mobile or 32-bit versions). If you experience other issues, please <a href="https://github.com/holoviz/panel/issues">report them</a>.
</div>"""
    else:
        source = """<div class="alert alert-block alert-success">
<em>Panelite</em> is powered by young technologies like <a href="https://pyodide.org/en/stable/">Pyodide</a> and <a href="https://jupyterlite.readthedocs.io/en/latest/">Jupyterlite</a>. Some browsers may be poorly supported (e.g. mobile or 32-bit versions). If you experience issues, please <a href="https://github.com/holoviz/panel/issues">report them</a>.
</div>"""
    info = nbformat.v4.new_markdown_cell(source=source)
    del info['id']
    return info

def convert_md_to_nb(
    filehandle, supported_syntax=('{pyodide}',)
) -> str:
    """
    Extracts Panel application code from a Markdown file.
    """
    nb = nbformat.v4.new_notebook()
    cells = nb['cells']
    inblock = False
    block_opener = None
    markdown, code = [], []
    while True:
        line = filehandle.readline()
        if not line:
            # EOF
            break

        # Remove MyST-Directives
        line = INLINE_DIRECTIVE.sub('', line)

        lsline = line.lstrip()
        if inblock:
            if lsline.startswith(block_opener):
                inblock = False
                code[-1] = code[-1].rstrip()
                code_cell = nbformat.v4.new_code_cell(source=''.join(code))
                code.clear()
                cells.append(code_cell)
            else:
                code.append(line)
        elif lsline.startswith("```"):
            num_leading_backticks = len(lsline) - len(lsline.lstrip("`"))
            block_opener = '`'*num_leading_backticks
            syntax = line.strip()[num_leading_backticks:]
            if syntax in supported_syntax:
                if markdown:
                    md_cell = nbformat.v4.new_markdown_cell(source=''.join(markdown))
                    markdown.clear()
                    nb['cells'].append(md_cell)
                inblock = True
            else:
                markdown.append(line)
        else:
            markdown.append(line)
    if markdown:
        md_cell = nbformat.v4.new_markdown_cell(source=''.join(markdown))
        nb['cells'].append(md_cell)
    return nb

def convert_docs():
    mds = (
        list(DOC_DIR.glob('getting_started/*.md')) +
        list(DOC_DIR.glob('explanation/**/*.md')) +
        list(DOC_DIR.glob('how_to/**/*.md'))
    )
    for md in mds:
        out = LITE_FILES / md.relative_to(DOC_DIR).with_suffix('.ipynb')
        out.parent.mkdir(parents=True, exist_ok=True)
        if md.suffix != '.md' or md.name == 'index.md':
            continue
        with open(md, encoding="utf-8") as mdf:
            nb = convert_md_to_nb(mdf)
        dependencies = _get_dependencies(md)
        if dependencies:
            install = _get_install_code_cell(dependencies=dependencies)
            nb['cells'].insert(0, install)
            info = _get_info_markdown_cell(md)
            nb['cells'].insert(0, info)
        with open(out, 'w', encoding='utf-8') as fout:
            nbformat.write(nb, fout)

def copy_examples():
    nbs = list(EXAMPLES_DIR.glob('*/*/*.ipynb')) + list(EXAMPLES_DIR.glob('*/*.*'))
    for nb in nbs:
        if ".ipynb_checkpoints" in str(nb):
            continue
        nbpath = pathlib.Path(nb)
        out = LITE_FILES / nbpath.relative_to(EXAMPLES_DIR)
        out.parent.mkdir(parents=True, exist_ok=True)

        if nb.suffix == '.ipynb':
            dependencies = _get_dependencies(nbpath)

            with open(nb, encoding='utf-8') as fin:
                nb = nbformat.read(fin, 4)
                if dependencies:
                    install = _get_install_code_cell(dependencies=dependencies)
                    nb['cells'].insert(0, install)

                info = _get_info_markdown_cell(nbpath)
                nb['cells'].insert(0, info)
            with open(out, 'w', encoding='utf-8') as fout:
                nbformat.write(nb, fout)
        elif not nb.is_dir():
            shutil.copyfile(nb, out)

def copy_assets():
    shutil.copytree(
        EXAMPLES_DIR / 'assets',
        LITE_FILES / 'assets',
        dirs_exist_ok=True
    )
    shutil.copytree(
        DOC_DIR / '_static',
        LITE_FILES / '_static',
        dirs_exist_ok=True
    )

if __name__=="__main__":
    convert_docs()
    copy_examples()
    copy_assets()
