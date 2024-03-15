"""Abstraction over the result of application of a spot detection procedure to an input image"""

import dataclasses
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    import numpy as np
    import pandas as pd

from ._constants import *
from ._exceptions import DimensionalityError

__author__ = "Vince Reuter"
__all__ = ["DetectionResult"]


# how to rename columns arising from extraction from skimage.measure.regionprops_table, to better suit downstream analysis
# TODO: consider making this configurable, see: https://github.com/gerlichlab/spotfishing/issues/1
ROI_CENTROID_COLUMN_RENAMING = tuple(
    (f"{ROI_CENTROID_KEY}-{i}", c) for i, c in enumerate(["zc", "yc", "xc"])
)

# the sequence of columns of fields extracted from skimage.measure.regionprops_table, after accounting for expansion in multiple dimensions (e.g., centroid_weighted)
SKIMAGE_REGIONPROPS_TABLE_COLUMNS_EXPANDED = [
    old for old, _ in ROI_CENTROID_COLUMN_RENAMING
] + [ROI_AREA_KEY, ROI_MEAN_INTENSITY_KEY]

# the expected column names in a detection result table, after extraction and renaming
DETECTION_RESULT_TABLE_COLUMNS = [
    dict(ROI_CENTROID_COLUMN_RENAMING).get(c, c)
    for c in SKIMAGE_REGIONPROPS_TABLE_COLUMNS_EXPANDED
]


@dataclasses.dataclass(frozen=True)
class DetectionResult:
    """
    The result of applying spot detection to an input image

    Parameters
    ----------
    table : pd.DataFrame
        The table of detected spot coordinates and measurements
    image : np.ndarray
        The image (after possibly some preprocessing) that was actually used in detection
    labels : np.ndarray
        The labels for the detected ROIs
    """

    table: "pd.DataFrame"
    image: "np.ndarray"
    labels: "np.ndarray"

    def __post_init__(self) -> None:
        """Validate that the structure and values of the inputs are as required."""
        errors = []
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
