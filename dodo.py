import os
if "PYCTDEV_ECOSYSTEM" not in os.environ:
    os.environ["PYCTDEV_ECOSYSTEM"] = "conda"

from pyctdev import *  # noqa: api
from pyctdev import CmdAction
from pyctdev._conda import _options_param, _channel_param, _conda_build_deps, _conda_install_with_options_hacked

def task_pip_on_conda():	
    """Experimental: provide pip build env via conda"""	
    return {'actions':[	
        # some ecosystem=pip build tools must be installed with conda when using conda...	
        'conda install -y pip twine wheel',	
        # ..and some are only available via conda-forge	
        'conda install -y -c conda-forge tox virtualenv',	
        # this interferes with pip-installed nose	
        'conda remove -y --force nose'	
    ]}


def _build_dev(channel):
    channels = " ".join(['-c %s' % c for c in channel])
    return "conda build %s conda.recipe/ --build-only" % channels


def task_develop_install():
    """python develop install, with specified optional groups of dependencies (installed by conda only).

    Typically ``conda install "test dependencies" && pip install -e . --no-deps``.

    Pass --options multiple times to specify other optional groups
    (see project's setup.py for available options).

    E.g.

    ``doit develop_install -o examples -o tests``
    ``doit develop_install -o all``

    """
    return {'actions': [
        CmdAction(_conda_build_deps),
        CmdAction(_conda_install_with_options_hacked),
        CmdAction(_build_dev),
        "conda install --use-local panel"],
            'params': [_options_param,_channel_param]}
