from packaging.version import Version
from param.depends import depends
from param.parameterized import transform_reference
from param.reactive import bind

from .config import __version__
from .util.warnings import deprecated


# Alias for backward compatibility
def param_value_if_widget(*args, **kwargs):
    if Version(Version(__version__).base_version) > Version('1.2'):
        deprecated("1.5", "param_value_if_widget", "transform_reference")
    return transform_reference(*args, **kwargs)

__all__ = ["bind", "depends"]
