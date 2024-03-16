"""Helpers for test functions/suites"""

import os
from pathlib import Path
import numpy as np


__author__ = "Vince Reuter"
__credits__ = ["Vince Reuter"]

__all__ = [
    "load_image_file",
]


def get_img_data_file(fn: str) -> Path:
    """Get the path to an input file (image data)."""
    return Path(os.path.dirname(__file__)) / "data" / "inputs" / fn


def load_image_file(fn: str) -> np.ndarray:
    """Load an input image from disk, with the given name and stored in test data inputs folder."""
    return np.load(get_img_data_file(fn))  # type: ignore
