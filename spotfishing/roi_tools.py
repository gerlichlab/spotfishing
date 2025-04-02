"""Tools for working with spots/ROIs"""

from typing import Any, Mapping, TypeAlias

from gertils.geometry import ImagePoint3D
from numpydoc_decorator import doc  # type: ignore[import-untyped]
from pandas import Series

from .detection_result import RoiCenterKeys

Record: TypeAlias = Series | Mapping[str, Any]  # type: ignore[misc,type-arg]


@doc(
    summary="Get region centroid from data row.",
    parameters=dict(rec="The data corresponding to a record from a file."),
    raises=dict(
        KeyError=(
            "If any of the required keys to parse coordinates isn't present in given"
            " row."
        )
    ),
    returns="Coordinates which define a point in a 3D image.",
)
def get_centroid_from_record(rec: Record) -> ImagePoint3D:  # noqa: D103
    z = rec[RoiCenterKeys.Z.value]
    y = rec[RoiCenterKeys.Y.value]
    x = rec[RoiCenterKeys.X.value]
    return ImagePoint3D(z=z, y=y, x=x)
