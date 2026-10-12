"""Different spot detection implementations"""

from dataclasses import dataclass
from typing import Annotated, Optional, Union, cast

import numpy as np
import numpy.typing as npt
import pandas as pd
from numpydoc_decorator import doc
from scipy import ndimage as ndi
from typing_extensions import Doc

from ._constants import ROI_AREA_KEY, ROI_CENTROID_KEY, ROI_MEAN_INTENSITY_KEY
from ._exceptions import DimensionalityError
from ._skimage import expand_labels, regionprops_table, remove_small_objects
from ._types import NumpyInt, PixelValue
from .detection_result import (
    SKIMAGE_REGIONPROPS_TABLE_COLUMNS_EXPANDED,
    SPOT_DETECTION_COLUMN_RENAMING,
    DetectionResult,
)
from .dog_transform import DifferenceOfGaussiansTransformation

__author__ = "Vince Reuter"
__credits__ = ["Vince Reuter", "Kai Sandoval Beckwith"]

__all__ = ["detect_spots_dog", "detect_spots_int"]

Numeric = Union[int, float]


@doc(summary="Parameter descriptions common to various spot detection procedures")
@dataclass(frozen=True)
class detection_signature:  # noqa: N801
    image = Annotated[npt.NDArray[PixelValue], Doc("3D image in which to detect spots")]
    threshold = Annotated[
        Numeric,
        Doc(
            "The minimum (after any transformations) pixel value required to regard a pixel as part of a spot"
        ),
    ]
    expand_px = Annotated[
        Optional[Numeric],
        Doc("The number of pixels by which to expand a detected and defined region"),
    ]
    result = Annotated[
        DetectionResult,
        Doc(
            "Bundle of table of ROI coordinates and data, the image used for spot detection, and region labels array"
        ),
    ]


@doc(
    summary="Detect spots by difference of Gaussians filter.",
    parameters=dict(
        transform="The subtraction-after-smoothing parameterisation that defined DoG",
    ),
    raises=dict(
        TypeError="If `input_image` isn't a numpy array, or the given `transform` isn't specifically a `DifferenceOfGaussiansTransformation`",
        DimensionalityError="If `input_image` isn't 3D",
    ),
)
def detect_spots_dog(  # noqa: D103
    input_image: detection_signature.image,
    *,
    spot_threshold: detection_signature.threshold,
    expand_px: detection_signature.expand_px,
    transform: DifferenceOfGaussiansTransformation,
) -> detection_signature.result:
    # Something from scikit-image, such as skimage.feature.blob_dog, could replace this; see
    # https://github.com/gerlichlab/spotfishing/issues/5
    _check_input_image(input_image)
    # Checked at run time, since callers may pass any type despite the annotation.
    if not isinstance(cast("object", transform), DifferenceOfGaussiansTransformation):
        raise TypeError(
            f"For DoG-based detection, the transformation must be of type {DifferenceOfGaussiansTransformation.__name__}; got {type(transform).__name__}"
        )
    img = transform(input_image)
    labels, _ = _label(img > spot_threshold)
    spot_props, labels = _build_props_table(
        labels=labels, input_image=input_image, expand_px=expand_px
    )
    return DetectionResult(table=spot_props, image=img, labels=labels)


@doc(
    summary="Detect spots by a simple pixel value threshold.",
    raises=dict(
        TypeError="If `input_image` isn't a numpy array",
        DimensionalityError="If `input_image` isn't 3D",
    ),
)
def detect_spots_int(  # noqa: D103
    input_image: detection_signature.image,
    *,
    spot_threshold: detection_signature.threshold,
    expand_px: detection_signature.expand_px,
) -> detection_signature.result:
    _check_input_image(input_image)
    binary = input_image > spot_threshold
    binary = ndi.binary_fill_holes(binary)
    struct = ndi.generate_binary_structure(input_image.ndim, 2)
    labels, num_obj = _label(binary, structure=struct)
    labels = remove_small_objects(labels, min_size=5) if num_obj > 1 else labels
    spot_props, labels = _build_props_table(
        labels=labels, input_image=input_image, expand_px=expand_px
    )
    return DetectionResult(table=spot_props, image=input_image, labels=labels)


def _label(
    mask: npt.NDArray[np.bool_],
    structure: Optional[npt.NDArray[np.bool_]] = None,
) -> tuple[npt.NDArray[NumpyInt], int]:
    """Label the connected regions of a mask, and count them.

    scipy returns both only when it is handed no array to write the labels into, as here;
    with one, it returns the count alone.
    """
    return cast("tuple[npt.NDArray[NumpyInt], int]", ndi.label(mask, structure=structure))


def _build_props_table(
    *,
    labels: npt.NDArray[NumpyInt],
    input_image: npt.NDArray[PixelValue],
    expand_px: Optional[Numeric],
) -> tuple[pd.DataFrame, npt.NDArray[NumpyInt]]:
    if expand_px:
        labels = expand_labels(labels, expand_px)
    if np.all(labels == 0):
        # No substructures (ROIs) exist.
        spot_props = pd.DataFrame(columns=SKIMAGE_REGIONPROPS_TABLE_COLUMNS_EXPANDED)
    else:
        spot_props = pd.DataFrame(
            regionprops_table(
                label_image=labels,
                intensity_image=input_image,
                properties=(ROI_CENTROID_KEY, ROI_AREA_KEY, ROI_MEAN_INTENSITY_KEY),
            )
        )
    spot_props = spot_props.rename(
        columns=dict(SPOT_DETECTION_COLUMN_RENAMING),
        inplace=False,
        errors="raise",
    )
    spot_props = spot_props.reset_index(drop=True)
    return spot_props, labels


def _check_input_image(img: npt.NDArray[PixelValue]) -> None:
    # Checked at run time, since callers may pass any type despite the annotation.
    if not isinstance(cast("object", img), np.ndarray):
        raise TypeError(f"Expected numpy array for input image but got {type(img).__name__}")
    if img.ndim != 3:  # noqa: PLR2004
        raise DimensionalityError(f"Expected 3D input image but got {img.ndim}-dimensional")
