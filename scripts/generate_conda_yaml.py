from __future__ import annotations

import argparse
import pathlib
import sys

import toml
import yaml

PROJECT_DATA = toml.load(
    pathlib.Path(__file__).parent.parent / 'pyproject.toml'
)['project']

PROJECT_MAP = {
    'graphviz': 'python-graphviz'
}

def normalize_dependency(dep):
    for proj, conda_dep in PROJECT_MAP.items():
        if proj in dep:
            dep = dep.replace(proj, conda_dep)
    return dep.replace('==', '=').replace(' =', '=').replace(' >', '>').replace(' <', '<')

def generate_yaml(
    name: str = None,
    python_version: str = '3.10',
    optional: List[str] | None = None,
    channels: List[str] | None = None,
    extras:   List[str] | None = None,
    pip_only: List[str] | None = None
):
    spec = {}
    if name:
        spec['name'] = name
    if channels:
        spec['channels'] = channels
    spec['dependencies'] = deps = [f'python={python_version}'] if python_version else []
    deps += ['pip']
    deps += [
        normalize_dependency(dep) for dep in PROJECT_DATA['dependencies']
    ]
    optional_deps = PROJECT_DATA['optional-dependencies']
    pip_deps = [dep for p in pip_only for dep in optional_deps[p]]
    for opt in (optional or []):
        if opt not in optional_deps:
            raise KeyError(f'Optional dependency group {opt!r} not found.')
        for dep in optional_deps[opt]:
            if dep not in pip_deps:
                deps.append(normalize_dependency(dep))
    for extra in (extras or []):
        if extra not in pip_deps:
            deps.append(normalize_dependency(extra))
    deps.append({'pip': pip_deps})
    return spec

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='conda environment.yml builder',
        description='This script generates a conda environment from the optional dependencies in a pyproject.toml',
    )
    parser.add_argument('-n', '--name', type=str)
    parser.add_argument('-p', '--python', type=str)
    parser.add_argument('-o', '--optional', nargs='+')
    parser.add_argument('-c', '--channel', nargs='+')
    parser.add_argument('-e', '--extras', nargs='+')
    parser.add_argument('--pip-only', nargs='+')

    args = parser.parse_args()
    env_yaml = generate_yaml(
        args.name, args.python, args.optional, args.channel, args.extras, args.pip_only
    )
    with open('environment.yaml', 'w', encoding='utf-8') as f:
        f.write(yaml.dump(env_yaml))
