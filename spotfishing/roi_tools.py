"""Tools for working with spots/ROIs"""

from typing import Mapping, TypeAlias

from gertils.geometry import ImagePoint3D
from numpydoc_decorator import doc  # type: ignore[import-untyped]
from pandas import Series

from .detection_result import RoiCenterKeys

Record: TypeAlias = Series | Mapping[str, object]  # type: ignore[explicit-any]


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
def get_centroid_from_record(  # pylint: disable=missing-function-docstring
    rec: Record,
) -> ImagePoint3D:  # noqa: D103
    return ImagePoint3D(
        z=rec[RoiCenterKeys.Z.value],  # type: ignore[arg-type]
        y=rec[RoiCenterKeys.Y.value],  # type: ignore[arg-type]
        x=rec[RoiCenterKeys.X.value],  # type: ignore[arg-type]
    )
