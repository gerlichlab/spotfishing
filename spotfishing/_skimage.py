"""The scikit-image functions spotfishing uses, typed.

scikit-image leaves most of its parameters and results unannotated, so pyright cannot
tell what these functions return. Each function here calls scikit-image's, with its
parameter names, and declares the types it takes and returns; the rest of the package
is checked against those. This module alone may use what pyright cannot type. Where
scikit-image does annotate, or pyright can infer, pyright still checks the declared
types against scikit-image's own.
"""

# pyright: reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownArgumentType=false

import inspect
from collections.abc import Sequence
from typing import Any, TypeVar, cast

import numpy as np
import numpy.typing as npt
from skimage import filters, measure, morphology, segmentation

from ._types import FloatImage

__all__ = [
    "ball",
    "expand_labels",
    "gaussian",
    "regionprops_table",
    "remove_small_objects",
    "white_tophat",
]

_Array = TypeVar("_Array", bound=npt.NDArray[Any])

# scikit-image 0.26 replaced the min_size of remove_small_objects, which removes the
# objects smaller than it, by max_size, which removes those no larger than it.
# spotfishing states the largest size to remove, as max_size does, and before 0.26
# passes the size above it as min_size.
_HAS_MAX_SIZE = (
    "max_size" in inspect.signature(morphology.remove_small_objects).parameters
)


def gaussian(image: npt.NDArray[Any], sigma: float) -> FloatImage:
    """Blur an image with a Gaussian of the given standard deviation."""
    return filters.gaussian(image, sigma)


def ball(radius: int) -> npt.NDArray[np.uint8]:
    """Make a ball-shaped footprint of the given radius."""
    # Without decomposition, scikit-image returns one array; pyright also infers the
    # tuple of decomposed footprints it returns with one.
    return cast("npt.NDArray[np.uint8]", morphology.ball(radius))


def white_tophat(image: _Array, footprint: npt.NDArray[Any]) -> _Array:
    """Subtract from an image its morphological opening by the footprint."""
    # Without an output array, scikit-image returns a new one; pyright also infers
    # None, the output array's default.
    return cast("_Array", morphology.white_tophat(image, footprint=footprint))


def remove_small_objects(
    ar: _Array,
    max_size: int,
) -> _Array:
    """Remove the labelled objects of the given size or smaller."""
    if _HAS_MAX_SIZE:
        return morphology.remove_small_objects(ar, max_size=max_size)
    return morphology.remove_small_objects(ar, min_size=max_size + 1)


def expand_labels(label_image: _Array, distance: float) -> _Array:
    """Expand the labelled regions by the given distance, without overlapping."""
    # scikit-image takes a float; pyright infers an int from the default distance of 1.
    return segmentation.expand_labels(
        label_image,
        distance,  # pyright: ignore[reportArgumentType]
    )


def regionprops_table(
    label_image: npt.NDArray[Any],
    intensity_image: npt.NDArray[Any],
    properties: Sequence[str],
) -> dict[str, npt.NDArray[Any]]:
    """Measure the given properties of each labelled region, one array per property."""
    return measure.regionprops_table(
        label_image, intensity_image=intensity_image, properties=properties
    )
