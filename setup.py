#!/usr/bin/env python
import json
import os
import sys

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
    'bokeh >=3.2.0,<3.4.0',
    'param >=2.0.0,<3.0',
    'pyviz_comms >=2.0.0',
    'xyzservices >=2021.09.1', # Bokeh dependency, but pyodide 23.0.0 does not always pick it up
    'markdown',
    'markdown-it-py',
    'linkify-it-py',
    'mdit-py-plugins',
    'requests',
    'tqdm >=4.48.0',
    'bleach',
    'typing_extensions',
    'pandas >=1.2',
]

_recommended = [
    'jupyterlab',
    'holoviews >=1.16.0',
    'matplotlib',
    'pillow',
    'plotly'
]

_tests_core = [
    # Test dependencies
    'flake8',
    'parameterized',
    'pytest',
    'nbval',
    'pytest-rerunfailures',
    'pytest-asyncio <0.22',
    'pytest-xdist',
    'pytest-cov',
    'pre-commit',
    'psutil',
    # Libraries tested in unit tests
    'altair',
    'anywidget',
    'folium',
    'diskcache',
    'holoviews >=1.16.0',
    'numpy',
    'pandas >=1.3',
    'ipython >=7.0',
    'scipy',
]

_tests = _tests_core + [
    'ipympl',
    'ipyvuetify',
    'ipywidgets_bokeh',
    'reacton',
    'twine',
    # Temporary pins
    'numba <0.58'
]

_ui = [
    'jupyter-server',
    'playwright',
    'pytest-playwright'
]

_examples = [
    'holoviews >=1.16.0',
    'hvplot',
    'plotly >=4.0',
    'altair',
    'streamz',
    'vega_datasets',
    'vtk',
    'scikit-learn',
    'datashader',
    'jupyter_bokeh >=3.0.7',
    'django <4',
    'channels',
    'pyvista',
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
    'python-graphviz',
    'xgboost',
    'ipyvuetify',
    'reacton',
    'scikit-image',
    'fastparquet'
]

# Anything only installable via conda
_conda_only = [
    'pygraphviz',
    'python-graphviz',
]

extras_require = {
    'examples': _examples,
    'tests_core': _tests_core,
    'tests': _tests,
    'recommended': _recommended,
    'doc': _recommended + [
        'nbsite >=0.8.4',
        'lxml',
        'pandas <2.1.0' # Avoid deprecation warnings
    ],
    'ui': _ui
}

extras_require['all'] = sorted(set(sum(extras_require.values(), [])))
extras_require['all_pip'] = sorted(set(extras_require['all']) - set(_conda_only))

# Superset of what's in pyproject.toml (includes non-python
# dependencies).  Also, pyproject.toml isn't supported by all tools
# anyway (e.g. older versions of pip, or conda - which also supports
# non-python dependencies). Note that setup_requires isn't used
# because it doesn't work well with pip.
extras_require['build'] = [
    'param >=2.0.0',
    'setuptools >=42',
    'requests',
    'packaging',
    'bokeh >=3.3.0,<3.4.0',
    'pyviz_comms >=2.0.0',
    'bleach',
    'markdown',
    'tqdm >=4.48.0',
    'cryptography <39', # Avoid pyOpenSSL issue
    'urllib3 <2.0',  # See: https://github.com/holoviz/panel/pull/4979
]

setup_args = dict(
    name='panel',
    version=get_setup_version("panel"),
    description='The powerful data exploration & web app framework for Python.',
    long_description=open('README.md', encoding="utf8").read() if os.path.isfile('README.md') else 'Consult README.md',
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
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
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
    python_requires=">=3.9",
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
