"""Tools for working with spots/ROIs"""

from collections.abc import Mapping
from typing import TypeAlias

from gertils.geometry import ImagePoint3D
from numpydoc_decorator import doc
from pandas import Series

from .detection_result import RoiCenterKeys

Record: TypeAlias = Series | Mapping[str, object]


@doc(
    summary="Get region centroid from data row.",
    parameters=dict(rec="The data corresponding to a record from a file."),
    raises=dict(
        KeyError="If any of the required keys to parse coordinates isn't present in given row."
    ),
    returns="Coordinates which define a point in a 3D image.",
)
def get_centroid_from_record(  # noqa: D103
    rec: Record,
) -> ImagePoint3D:
    return ImagePoint3D(
        z=rec[RoiCenterKeys.Z.value],  # pyright: ignore[reportArgumentType]
        y=rec[RoiCenterKeys.Y.value],  # pyright: ignore[reportArgumentType]
        x=rec[RoiCenterKeys.X.value],  # pyright: ignore[reportArgumentType]
    )
