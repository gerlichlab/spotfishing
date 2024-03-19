"""Helpers for test functions/suites"""

import os
from pathlib import Path
from typing import Union

import numpy as np

from spotfishing_looptrace import DifferenceOfGaussiansSpecificationForLooptrace

__author__ = "Vince Reuter"
__credits__ = ["Vince Reuter"]

__all__ = [
    "ORIGINAL_SPECIFICATION",
    "get_img_data_file",
    "load_image_file",
]

Numeric = Union[float, int]


# original parameterisation of the transformation for detection with DoG
ORIGINAL_SPECIFICATION = DifferenceOfGaussiansSpecificationForLooptrace(
    apply_white_tophat=True,
    sigma_narrow=0.8,
    sigma_wide=1.3,
    sigma_post_divide=3,
    standardise=True,
)


def get_img_data_file(fn: str) -> Path:
    """Get the path to an input file (image data)."""
    return Path(os.path.dirname(__file__)) / "data" / "inputs" / fn


def load_image_file(fn: str) -> np.ndarray:
    """Load an input image from disk, with the given name and stored in test data inputs folder."""
    return np.load(get_img_data_file(fn))  # type: ignore
