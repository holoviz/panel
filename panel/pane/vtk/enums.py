from enum import Enum

from ...util import public

@public
class SCALAR_MODE(Enum):
    Default = 0
    UsePointData = 1
    UseCellData = 2
    UsePointFieldData = 3
    UseCellFieldData = 4
    UseFieldData = 5


@public
class COLOR_MODE(Enum):
    DirectScalars = 0
    MapScalars = 1


@public
class ACCESS_MODE(Enum):
    ById = 0
    ByName = 1
