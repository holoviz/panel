import os

if "PYCTDEV_ECOSYSTEM" not in os.environ:
    os.environ["PYCTDEV_ECOSYSTEM"] = "conda"

from pyctdev import *  # noqa: api


def task_pip_on_conda():
    """Experimental: provide pip build env via conda"""
    return {'actions':[
        # some ecosystem=pip build tools must be installed with conda when using conda...
        'conda install -y pip twine wheel "rfc3986>=1.4.0"',
        # ..and some are only available via conda-forge
        'conda install -y -c conda-forge tox "virtualenv<=20.4.7"',
    ]}


def _build_dev(channel):
    channels = " ".join(['-c %s' % c for c in channel])
    return "conda build %s conda.recipe/ --build-only" % channels
