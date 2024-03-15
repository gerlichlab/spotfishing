"""Package-level members"""

from .detectors import detect_spots_dog, detect_spots_int
from .exceptions import *

__author__ = "Vince Reuter"
__credits__ = ["Vince Reuter", "Kai Sandoval Beckwith"]

__all__ = ["detect_spots_dog", "detect_spots_int", "DimensionalityError"]
