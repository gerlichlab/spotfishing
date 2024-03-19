"""Helpers for test functions/suites"""

import os
from pathlib import Path
from typing import Union

import numpy as np
from skimage.morphology import ball, white_tophat

from spotfishing import DifferenceOfGaussiansTransformation as DogTransform
from spotfishing.dog_transform import ImageEndomorphism, ImageMorphism21, div_by_gauss

__author__ = "Vince Reuter"
__credits__ = ["Vince Reuter"]

__all__ = [
    "ORIGINAL_TRANSFORM",
    "get_img_data_file",
    "load_image_file",
]

Numeric = Union[float, int]


# original parameterisation of the transformation for detection with DoG
ORIGINAL_TRANSFORM = DogTransform(
    pre_diff=ImageEndomorphism(white_tophat, dict(footprint=ball(2))),
    sigma_narrow=0.8,
    sigma_wide=1.3,
    post_diff=ImageMorphism21(div_by_gauss, dict(sigma=3)),
    standardise=True,
)


def get_img_data_file(fn: str) -> Path:
    """Get the path to an input file (image data)."""
    return Path(os.path.dirname(__file__)) / "data" / "inputs" / fn


def load_image_file(fn: str) -> np.ndarray:
    """Load an input image from disk, with the given name and stored in test data inputs folder."""
    return np.load(get_img_data_file(fn))  # type: ignore
