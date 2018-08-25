import param

from .layout import Row, Column # noqa
from .panels import Panel # noqa

__version__ = str(param.version.Version(fpath=__file__, archive_commit="$Format:%h$",
                                        reponame="panel"))


