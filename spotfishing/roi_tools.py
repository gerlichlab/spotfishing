"""Tools for working with spots/ROIs"""

from collections.abc import Mapping

from gertils.geometry import ImagePoint3D
from pandas import Series

from .detection_result import RoiCenterKeys

# A plain assignment, not a `type` statement: at run time it stays the union, as it
# was in v0.4.1, so typing.get_args finds the types a record may have.
Record = Series | Mapping[str, object]


def get_centroid_from_record(
    rec: Record,
) -> ImagePoint3D:
    """Get region centroid from data row.

    Parameters
    ----------
    rec : Series or Mapping[str, object]
        The data corresponding to a record from a file.

    Returns
    -------
    ImagePoint3D
        Coordinates which define a point in a 3D image.

    Raises
    ------
    KeyError
        If any of the required keys to parse coordinates isn't present in
        given row.

    """
    return ImagePoint3D(
        z=rec[RoiCenterKeys.Z.value],  # pyright: ignore[reportArgumentType]
        y=rec[RoiCenterKeys.Y.value],  # pyright: ignore[reportArgumentType]
        x=rec[RoiCenterKeys.X.value],  # pyright: ignore[reportArgumentType]
    )
