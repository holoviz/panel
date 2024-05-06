import json
import pathlib


def convert_notebook_to_md(filename, directive='{pyodide}'):
    with open(filename, encoding='utf-8') as nb:
        nb_json = json.loads(nb.read())

    md = f"# {filename.name[:-6].replace('_', ' ').title()}"
    for cell in nb_json['cells']:
        ctype = cell['cell_type']
        if ctype == 'raw':
            continue
        if md:
            md += '\n\n'
        source = cell['source']
        if ctype == 'code':
            md += f'```{directive}\n'
        for src in source:
            md += src
        if ctype == 'code':
            md += '\n```'
    return md

if __name__ == '__main__':
    ROOT = pathlib.Path(__file__).parents[2]
    GALLERY = ROOT / 'doc' / 'gallery'
    for nb in ROOT.glob('./examples/gallery/*.ipynb'):
        md = convert_notebook_to_md(nb)
        with open(GALLERY / f'{nb.name[:-6]}.md', 'w', encoding='utf-8') as f:
            f.write(md)
