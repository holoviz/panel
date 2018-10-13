#!/usr/bin/env python

import os
from setuptools import setup, find_packages


def get_setup_version(reponame):
    """
    Helper to get the current version from either git describe or the
    .version file (if available).
    """
    import json
    basepath = os.path.split(__file__)[0]
    version_file_path = os.path.join(basepath, reponame, '.version')
    try:
        from param import version
    except:
        version = None
    if version is not None:
        return version.Version.setup_version(basepath, reponame, archive_commit="$Format:%h$")
    else:
        print("WARNING: param>=1.6.0 unavailable. If you are installing a package, this warning can safely be ignored. If you are creating a package or otherwise operating in a git repository, you should install param>=1.6.0.")
        return json.load(open(version_file_path, 'r'))['version_string']


########## dependencies ##########

install_requires = [
    'bokeh >=0.12.15',
    'param >=1.8.1',
    'pyviz_comms >=0.6.0',
    'markdown',
    'testpath<0.4' # temporary due to pip issue?
]

_recommended = [
    'notebook >=5.4',
    'holoviews>=1.11.0a8',
    'matplotlib',
    'pillow',
    'plotly'
]

extras_require = {
    'tests': [
        'coveralls',
        'nose',
        'flake8',
        'parameterized',
        'pytest',
        'scipy',
        'nbsmoke >=0.2.0',
        'pytest-cov',
        'codecov',
        # For Panes.ipynb
        'plotly',
        'altair',
        'vega_datasets'
    ],
    'recommended': _recommended,
    'doc': _recommended + [
        'nbsite',
        'sphinx_ioam_theme'
    ]
}

extras_require['all'] = sorted(set(sum(extras_require.values(), [])))

# until pyproject.toml/equivalent is widely supported (setup_requires
# doesn't work well with pip)
extras_require['build'] = [
    'param >=1.7.0',
    'pyct >=0.4.4',
    'setuptools >=30.3.0'
]

setup_args = dict(
    name='panel',
    version=get_setup_version("panel"),
    description='A high level dashboarding library for python visualization libraries.',
    long_description=open('README.md').read() if os.path.isfile('README.md') else 'Consult README.md',
    long_description_content_type="text/markdown",
    author= "PyViz developers",
    author_email= "developers@pyviz.org",
    maintainer= "PyViz",
    maintainer_email= "developers@pyviz.org",
    platforms=['Windows', 'Mac OS X', 'Linux'],
    license='BSD',
    url='http://pyviz.org',
    packages=find_packages(),
    package_data={'panel.models': ['*.ts']},
    include_package_data=True,
    classifiers = [
        "License :: OSI Approved :: BSD License",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries"],
    python_requires=">=2.7",
    install_requires=install_requires,
    extras_require=extras_require,
    tests_require=extras_require['tests']
)


if __name__=="__main__":
    setup(**setup_args)
