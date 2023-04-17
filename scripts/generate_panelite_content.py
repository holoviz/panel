"""
Helper script to convert and copy example notebooks into JupyterLite build.
"""
import hashlib
import json
import os
import pathlib
import shutil

import bokeh.sampledata
import nbformat

from test_panelite.notebooks_with_panelite_issues import NOTEBOOK_ISSUES

PANEL_BASE = pathlib.Path(__file__).parent.parent
EXAMPLES_DIR = PANEL_BASE / 'examples'
DEFAULT_DEPENDENCIES = ["panel"]

# Add piplite command to notebooks
with open(PANEL_BASE/"scripts"/"generate_panelite_content.json", "r", encoding="utf8") as file:
    DEPENDENCIES = json.load(file)

class DependencyNotFound(Exception):
    """Raised if a dependency cannot be found"""

def _notebook_key(nbpath: pathlib.Path):
    return str(nbpath).replace("\\", "/").split("examples/")[-1]

def _get_dependencies(nbpath: pathlib.Path):
    key = _notebook_key(nbpath)
    try:
        dependencies = DEPENDENCIES[key]
    except KeyError as ex:
        print(f"WARNING: Could not find the dependencies for '{key}'. Please add them")
        dependencies = DEFAULT_DEPENDENCIES
    return dependencies

def _to_piplite_install_code(dependencies):
    dependencies = [f"'{dependency}'" for dependency in dependencies]
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
        try:
            _, library, _, _, id = issue.split("/")
        except:
            breakpoint()
        if library == "panel":
            return f"#{id}"
        return f"{library}#{id}"
    return issue

def _get_info_markdown_cell(nbpath):
    key = _notebook_key(nbpath)
    issues = _get_issues(key)
    if issues:
        issues_str = ", ".join([f'<a href="{issue}">{_to_issue_str(issue)}</a>' for issue in issues])
        print(issues_str)
        source = f"""<div class="alert alert-block alert-danger">
This notebook is not expected to run successfully in <em>Panelite</em>. It has the following known issues: {issues_str}.

Panelite is powered by young technologies like <a href="https://pyodide.org/en/stable/">Pyodide</a> and <a href="https://jupyterlite.readthedocs.io/en/latest/">Jupyterlite</a>. Panelite does not work well in Edge. If you experience other issues, please <a href="https://github.com/holoviz/panel/issues">report them</a>.
</div>"""
    else:
        source = """<div class="alert alert-block alert-success">
This notebook is expected to run successfully in <em>Panelite</em>.

Panelite is powered by young technologies like <a href="https://pyodide.org/en/stable/">Pyodide</a> and <a href="https://jupyterlite.readthedocs.io/en/latest/">Jupyterlite</a>. Panelite does not work well in Edge. If you do experience issues, please <a href="https://github.com/holoviz/panel/issues">report them</a>.
</div>"""
    info = nbformat.v4.new_markdown_cell(source=source)
    del info['id']
    return info

def copy_examples():
    nbs = list(EXAMPLES_DIR.glob('*/*/*.ipynb')) + list(EXAMPLES_DIR.glob('*/*.*'))
    for nb in nbs:
        if ".ipynb_checkpoints" in str(nb):
            continue
        nbpath = pathlib.Path(nb)
        out = (PANEL_BASE / 'lite/files') / nbpath.relative_to(EXAMPLES_DIR)
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
        PANEL_BASE / 'lite' / 'files' / 'assets',
        dirs_exist_ok=True
    )

def download_sample_data():
    """
    Download larger data sets for various Bokeh examples.
    """
    from bokeh.util.sampledata import _download_file

    data_dir = PANEL_BASE / 'lite' / 'files' / 'assets' / 'sampledata'
    data_dir.mkdir(parents=True, exist_ok=True)

    s3 = 'http://sampledata.bokeh.org'
    files = json.loads((pathlib.Path(bokeh.util.sampledata.__file__).parent / 'sampledata.json').read_text())

    for filename, md5 in files:
        real_name, ext = os.path.splitext(filename)
        if ext == '.zip':
            if not os.path.splitext(real_name)[1]:
                real_name += ".csv"
        else:
            real_name += ext
        real_path = data_dir / real_name

        if real_path.is_file():
            local_md5 = hashlib.md5(open(real_path,'rb').read()).hexdigest()
            if local_md5 == md5:
                print(f"Skipping {filename!r} (checksum match)")
                continue
            else:
                print(f"Re-fetching {filename!r} (checksum mismatch)")
        _download_file(s3, filename, data_dir, progress=False)

if __name__=="__main__":
    copy_examples()
    # copy_assets()
    # download_sample_data()
