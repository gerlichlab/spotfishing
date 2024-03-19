"""Aliases for numeric types"""

from typing import Union

import numpy as np

__author__ = "Vince Reuter"
__credits__ = ["Vince Reuter"]

__all__ = ["NumpyInt", "NumpyFloat", "PixelValue"]

NumpyFloat = Union[np.float16, np.float32, np.float64]
NumpyInt = Union[np.int8, np.int16, np.int32, np.int64]
PixelValue = Union[np.int8, np.int16]
