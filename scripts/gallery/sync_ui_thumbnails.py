"""Copy reference thumbnails into the Panel UI gallery's S3 prefix."""

import inspect
import json
import subprocess

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from types import SimpleNamespace

import panel.ui as ui

from doc._ext.ui_reference import SECTIONS, _material_examples
from panel.viewable import Viewable

BUCKET = 'assets.holoviz.org'
DESTINATION = 'panel/thumbnails/reference/ui'


def object_keys(prefix):
    keys = set()
    token = None
    while True:
        command = ['aws', 's3api', 'list-objects-v2', '--bucket', BUCKET, '--prefix', prefix, '--output', 'json']
        if token:
            command.extend(['--continuation-token', token])
        result = subprocess.run(command, capture_output=True, check=True, text=True)
        listing = json.loads(result.stdout)
        keys.update(obj['Key'] for obj in listing.get('Contents', []))
        token = listing.get('NextContinuationToken')
        if not token:
            return keys


def thumbnail_sources(material):
    for module_name, section in SECTIONS.items():
        module = getattr(ui, module_name)
        for name in sorted(ui.__all__):
            component = getattr(ui, name)
            if (getattr(module, name, None) is not component
                or not inspect.isclass(component) or not issubclass(component, Viewable)):
                continue
            material_section = 'page' if section == 'templates' else section
            notebook = material / material_section / f'{name}.ipynb'
            if not notebook.is_file():
                notebook = material / material_section / f'{component.__name__}.ipynb'
            if not notebook.is_file():
                notebook = next((candidate for other in ('widgets', 'indicators', 'menus')
                                 if (candidate := material / other / f'{component.__name__}.ipynb').is_file()), notebook)
            if notebook.is_file():
                source = f'panel-material-ui/thumbnails/reference/{notebook.relative_to(material).with_suffix(".png")}'
            else:
                source = f'panel/thumbnails/reference/{section}/{name}.png'
            yield source, f'{DESTINATION}/{section}/{name}.png'


def resolve_source(source, keys):
    if source in keys:
        return source
    prefix, _, basename = source.rpartition('/')
    candidates = [f'{prefix.rsplit("/", 1)[0]}/{section}/{basename}'
                  for section in ('widgets', 'indicators', 'panes', 'layouts', 'global', 'templates', 'page', 'menus')]
    return next((key for key in candidates if key in keys), None)


def main():
    app = SimpleNamespace(config=SimpleNamespace(ui_reference_pmui_source=None))
    material = _material_examples(app)
    if material is None:
        raise FileNotFoundError('PMUI reference notebooks are unavailable')
    try:
        copies = list(thumbnail_sources(material))
        keys = object_keys('panel/thumbnails/reference/') | object_keys('panel-material-ui/thumbnails/reference/')
        existing = object_keys(f'{DESTINATION}/')
        remaining = []
        missing = []
        for source, target in copies:
            if target in existing:
                continue
            if resolved := resolve_source(source, keys):
                remaining.append((resolved, target))
            else:
                missing.append(target)

        if missing:
            from nbsite.gallery.gen import NO_IMAGE_THUMB

            placeholder = Path(NO_IMAGE_THUMB)
            print(f'No source thumbnail for {len(missing)} components; uploading {placeholder.name} instead.')
            for target in missing:
                subprocess.run(['aws', 's3', 'cp', str(placeholder), f's3://{BUCKET}/{target}',
                                '--only-show-errors'], check=True)

        def copy(source, target):
            subprocess.run(['aws', 's3', 'cp', f's3://{BUCKET}/{source}', f's3://{BUCKET}/{target}',
                            '--only-show-errors'], check=True)

        with ThreadPoolExecutor(max_workers=8) as pool:
            jobs = {pool.submit(copy, source, target): (source, target) for source, target in remaining}
            for job in as_completed(jobs):
                job.result()
        print(f'Copied {len(remaining)} source and {len(missing)} placeholder thumbnails for {len(copies)} components to s3://{BUCKET}/{DESTINATION}/')
    finally:
        if temporary := getattr(app, '_pmui_reference_dir', None):
            temporary.cleanup()


if __name__ == '__main__':
    main()
