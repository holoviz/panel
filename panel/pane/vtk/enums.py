
from enum import Enum


class SCALAR_MODE(Enum):
    Default = 0
    UsePointData = 1
    UseCellData = 2
    UsePointFieldData = 3
    UseCellFieldData = 4
    UseFieldData = 5


class COLOR_MODE(Enum):
    DirectScalars = 0
    MapScalars = 1


class ACCESS_MODE(Enum):
    ById = 0
    ByName = 1
