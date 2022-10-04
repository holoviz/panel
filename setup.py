#!/usr/bin/env python
import json
import os
import shutil
import sys

import pyct.build

from setuptools import find_packages, setup
from setuptools.command.develop import develop
from setuptools.command.install import install
from setuptools.command.sdist import sdist

PANEL_LITE_BUILD = 'PANEL_LITE' in os.environ


def get_setup_version(reponame):
    """
    Helper to get the current version from either git describe or the
    .version file (if available).
    """
    basepath = os.path.split(__file__)[0]
    version_file_path = os.path.join(basepath, reponame, '.version')
    try:
        from param import version
    except Exception:
        version = None
    if version is not None:
        return version.Version.setup_version(basepath, reponame, archive_commit="$Format:%h$")
    else:
        print("WARNING: param>=1.6.0 unavailable. If you are installing a package, "
              "this warning can safely be ignored. If you are creating a package or "
              "otherwise operating in a git repository, you should install param>=1.6.0.")
        return json.load(open(version_file_path, 'r'))['version_string']


def _build_paneljs():
    from bokeh.ext import build

    from panel.compiler import bundle_resources
    print("Building custom models:")
    panel_dir = os.path.join(os.path.dirname(__file__), "panel")
    build(panel_dir)
    print("Bundling custom model resources:")
    bundle_resources()
    if sys.platform != "win32":
        # npm can cause non-blocking stdout; so reset it just in case
        import fcntl
        flags = fcntl.fcntl(sys.stdout, fcntl.F_GETFL)
        fcntl.fcntl(sys.stdout, fcntl.F_SETFL, flags&~os.O_NONBLOCK)


class CustomDevelopCommand(develop):
    """Custom installation for development mode."""

    def run(self):
        if not PANEL_LITE_BUILD:
            _build_paneljs()
        develop.run(self)


class CustomInstallCommand(install):
    """Custom installation for install mode."""

    def run(self):
        if not PANEL_LITE_BUILD:
            _build_paneljs()
        install.run(self)


class CustomSdistCommand(sdist):
    """Custom installation for sdist mode."""

    def run(self):
        if not PANEL_LITE_BUILD:
            _build_paneljs()
        sdist.run(self)


_COMMANDS = {
    'develop': CustomDevelopCommand,
    'install': CustomInstallCommand,
    'sdist':   CustomSdistCommand,
}

try:
    from wheel.bdist_wheel import bdist_wheel

    class CustomBdistWheelCommand(bdist_wheel):
        """Custom bdist_wheel command to force cancelling qiskit-terra wheel
        creation."""

        def run(self):
            """Do nothing so the command intentionally fails."""
            if not PANEL_LITE_BUILD:
                _build_paneljs()
            bdist_wheel.run(self)

    _COMMANDS['bdist_wheel'] = CustomBdistWheelCommand
except Exception:
    pass

########## dependencies ##########

install_requires = [
    'bokeh >=2.4.0,<2.5.0',
    'param >=1.12.0',
    'pyviz_comms >=0.7.4',
    'markdown',
    'requests',
    'tqdm >=4.48.0',
    'pyct >=0.4.4',
    'bleach',
    'setuptools',
    'typing_extensions'
]

_recommended = [
    'jupyterlab',
    'holoviews >1.14.1',
    'matplotlib',
    'pillow',
    'plotly'
]

_tests = [
    # Test dependencies
    'flake8',
    'parameterized',
    'pytest',
    'nbval',
    'flaky',
    'pytest-xdist',
    'pytest-cov',
    'pre-commit',
    # Libraries tested in unit tests
    'folium',
    'ipympl',
    'scipy',
    'twine',
    'pandas >=1.3',
    'ipython >=7.0',
    'holoviews',
    'diskcache',
    "markdown-it-py",
    # Temporary pins (jupyter_bokeh needs updates)
    'ipywidgets <8.0'
]

_ui = [
    'playwright',
    'pytest-playwright'
]

extras_require = {
    'examples': [
        'hvplot',
        'plotly >=4.0',
        'altair',
        'streamz',
        'vega_datasets',
        'vtk ==9.0.1',
        'scikit-learn',
        'datashader',
        'jupyter_bokeh >=3.0.2',
        'django <4',
        'channels',
        'pyvista<0.33',
        'ipywidgets',
        'ipywidgets_bokeh',
        'ipyvolume',
        'ipyleaflet',
        'ipympl',
        'folium',
        'xarray',
        'pyinstrument >=4.0',
        'aiohttp',
        'croniter',
        'graphviz',
        'networkx >=2.5',
        'pygraphviz',
        'seaborn',
        'pydeck',
        'graphviz',
        'lxml',
        'python-graphviz',
        'xgboost'
    ],
    'tests': _tests,
    'recommended': _recommended,
    'doc': _recommended + [
        'nbsite >=0.7.2rc2',
        'pydata-sphinx-theme <=0.9.0',
        'sphinx-copybutton',
        'sphinx-design',
    ],
    'ui': _ui
}

extras_require['all'] = sorted(set(sum(extras_require.values(), [])))

# Superset of what's in pyproject.toml (includes non-python
# dependencies).  Also, pyproject.toml isn't supported by all tools
# anyway (e.g. older versions of pip, or conda - which also supports
# non-python dependencies). Note that setup_requires isn't used
# because it doesn't work well with pip.
extras_require['build'] = [
    'param >=1.9.2',
    'pyct >=0.4.4',
    'setuptools >=42',
    'bokeh >=2.4.3',
    'pyviz_comms >=0.6.0',
    'bleach',
    'tqdm',
    'twine',
    'rfc3986>=1.4.0'
]

setup_args = dict(
    name='panel',
    version=get_setup_version("panel"),
    description='A high level app and dashboarding solution for Python.',
    long_description=open('README.md').read() if os.path.isfile('README.md') else 'Consult README.md',
    long_description_content_type="text/markdown",
    author="HoloViz",
    author_email="developers@holoviz.org",
    maintainer="HoloViz",
    maintainer_email="developers@holoviz.org",
    platforms=['Windows', 'Mac OS X', 'Linux'],
    license='BSD',
    url='http://panel.holoviz.org',
    project_urls={
        'Source': 'https://github.com/holoviz/panel',
    },
    cmdclass=_COMMANDS,
    packages=find_packages(),
    include_package_data=True,
    data_files=[
        # like `jupyter serverextension enable --sys-prefix`
        (
            "etc/jupyter/jupyter_notebook_config.d",
            ["jupyter-config/jupyter_notebook_config.d/panel-client-jupyter.json"],
        ),
        # like `jupyter server extension enable --sys-prefix`
        (
            "etc/jupyter/jupyter_server_config.d",
            ["jupyter-config/jupyter_server_config.d/panel-client-jupyter.json"],
        ),
    ],
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Legal Industry",
        "Intended Audience :: Other Audience",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Office/Business",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries"],
    python_requires=">=3.7",
    entry_points={
        'console_scripts': [
            'panel = panel.command:main'
        ]
    },
    install_requires=install_requires,
    extras_require=extras_require,
    tests_require=extras_require['tests']
)

def clean_js_version(version):
    version = version.replace('-', '')
    for dev in ('a', 'b', 'rc'):
        version = version.replace(dev+'.', dev)
    return version

if __name__ == "__main__":
    example_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'panel', 'examples')

    if 'develop' not in sys.argv and 'egg_info' not in sys.argv:
        pyct.build.examples(example_path, __file__, force=True)

    version = setup_args['version']
    if 'post' not in version:
        with open('./panel/package.json') as f:
            package_json = json.load(f)
        js_version = package_json['version']
        version = version.split('+')[0]
        if any(dev in version for dev in ('a', 'b', 'rc')) and not '-' in js_version:
            raise ValueError(f"panel.js dev versions ({js_version}) must "
                             "must separate dev suffix with a dash, e.g. "
                             "v1.0.0rc1 should be v1.0.0-rc.1.")
        if version != 'None' and version != clean_js_version(js_version):
            raise ValueError(f"panel.js version ({js_version}) does not match "
                             f"panel version ({version}). Cannot build release.")

    setup(**setup_args)

    if os.path.isdir(example_path):
        shutil.rmtree(example_path)
