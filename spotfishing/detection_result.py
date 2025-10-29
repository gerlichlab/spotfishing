"""Abstraction over the result of application of a spot detection procedure to an input image"""

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Iterable

from numpydoc_decorator import doc  # type: ignore[import-untyped]

if TYPE_CHECKING:
    import numpy.typing as npt
    import pandas as pd

from ._constants import (
    ROI_AREA_KEY,
    ROI_CENTROID_KEY,
    ROI_MEAN_INTENSITY_KEY,
    ROI_MEAN_INTENSITY_KEY_CAMEL_CASE,
)
from ._exceptions import DimensionalityError
from ._types import NumpyInt, PixelValue

__author__ = "Vince Reuter"
__all__ = ["DetectionResult"]


class RoiCenterKeys(Enum):
    """A collection of the keys (column names) in a table from which to get (z, y, x)"""

    Z = "zc"
    Y = "yc"
    X = "xc"

    @classmethod
    def to_list(cls) -> list[str]:  # pylint: disable=missing-function-docstring
        return [m.value for m in cls]


# how to rename columns arising from extraction from skimage.measure.regionprops_table, to better suit downstream analysis
SPOT_DETECTION_COLUMN_RENAMING: tuple[tuple[str, str], ...] = tuple(
    (f"{ROI_CENTROID_KEY}-{i}", c) for i, c in enumerate(RoiCenterKeys.to_list())
) + (
    (ROI_AREA_KEY, ROI_AREA_KEY),
    (ROI_MEAN_INTENSITY_KEY, ROI_MEAN_INTENSITY_KEY_CAMEL_CASE),
)

# the sequence of columns of fields extracted from skimage.measure.regionprops_table, after accounting for expansion in multiple dimensions (e.g., centroid_weighted)
SKIMAGE_REGIONPROPS_TABLE_COLUMNS_EXPANDED = [
    old for old, _ in SPOT_DETECTION_COLUMN_RENAMING
]

# the expected column names in a detection result table, after extraction and renaming
DETECTION_RESULT_TABLE_COLUMNS = [new for _, new in SPOT_DETECTION_COLUMN_RENAMING]


@doc(
    summary="The result of applying spot detection to an input image",
    parameters=dict(
        table="A table of detected spot coordinates and measurements",
        image="The image (after possibly some preprocessing) that was actually used in detection",
        labels="Array of the same size/shape as the image, with nonnegative integer entries; a zero indicates that the pixel isn't in an ROI, and a nonzero indicates the index of the ROI to which the pixel's been assigned",
    ),
)
@dataclass(frozen=True, kw_only=True)
class DetectionResult:  # pylint: disable=missing-class-docstring
    table: "pd.DataFrame"
    image: "npt.NDArray[PixelValue]"
    labels: "npt.NDArray[NumpyInt]"

    def __post_init__(self) -> None:
        """Validate that the structure and values of the inputs are as required."""
        errors: list[Exception] = []
        cols = list(self.table.columns)
        if cols != DETECTION_RESULT_TABLE_COLUMNS:
            errors.append(IllegalDetectionResultTableColumns(observed_columns=cols))
        if self.image.ndim != 3:
            errors.append(
                DimensionalityError(
                    "{self.image.ndim}-dimensional (not 3!) image in spot detection result wrapper"
                )
            )
        if errors:
            raise IllegalDetectionResult(errors=[str(e) for e in errors])


class IllegalDetectionResult(Exception):
    """Aggregation of errors in trying to build a spot detection result"""

    def __init__(self, *, errors: Iterable[str]) -> None:
        errors = list(errors)
        if len(errors) == 0:
            raise ValueError(
                "Cannot create an illegal detection result error without at least one error message!"
            )
        super().__init__(
            f"{len(errors)} error(s) creating spot detection result: {'; '.join(errors)}"
        )


class IllegalDetectionResultTableColumns(Exception):
    """Error subtype for when detection result table columns aren't as expected"""

    def __init__(self, *, observed_columns: list[str]) -> None:
        super().__init__(
            f"Table columns don't match expectation: {observed_columns} != {DETECTION_RESULT_TABLE_COLUMNS}"
        )
