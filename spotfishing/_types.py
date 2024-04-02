"""Aliases for numeric types"""

from typing import Callable, Union

import numpy as np
import numpy.typing as npt

__author__ = "Vince Reuter"
__credits__ = ["Vince Reuter"]

__all__ = ["NumpyInt", "NumpyFloat", "PixelValue"]


Image = npt.NDArray["PixelValue"]

ImageEndomorphism = Callable[[Image], Image]

NumpyFloat = Union[np.float16, np.float32, np.float64]

NumpyInt = Union[np.int8, np.int16, np.int32, np.int64]

PixelValue = Union[np.uint8, np.uint16]
