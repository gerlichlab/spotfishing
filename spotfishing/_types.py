"""Aliases for numeric types"""

from typing import Any, Callable, Union

import numpy as np
import numpy.typing as npt

__author__ = "Vince Reuter"
__credits__ = ["Vince Reuter"]

__all__ = ["FloatImage", "NumpyInt", "NumpyFloat", "PixelValue"]


Image = npt.NDArray["PixelValue"]

# What filtering an image gives: its pixels as floating-point numbers.
FloatImage = npt.NDArray[np.floating[Any]]

ImageEndomorphism = Callable[[Image], Image]

NumpyFloat = Union[np.float16, np.float32, np.float64]

NumpyInt = Union[np.int8, np.int16, np.int32, np.int64]

PixelValue = Union[np.uint8, np.uint16]
