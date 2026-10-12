"""Package-level members"""

from ._numpy_compatibility import warn_of_releases_built_for_numpy_1

# Before the imports below load pandas, scipy and scikit-image, which fail with numpy 2 if built
# for numpy 1, say which to upgrade.
warn_of_releases_built_for_numpy_1()

from ._constants import ROI_AREA_KEY, ROI_MEAN_INTENSITY_KEY_CAMEL_CASE

# Importable from the package, though __all__ leaves it out; the alias tells pyright it is re-exported.
from ._constants import ROI_MEAN_INTENSITY_KEY as ROI_MEAN_INTENSITY_KEY  # noqa: PLC0414
from ._exceptions import DimensionalityError
from .detection_result import DetectionResult, RoiCenterKeys
from .detectors import detect_spots_dog, detect_spots_int
from .dog_transform import DifferenceOfGaussiansTransformation

__author__ = "Vince Reuter"
__credits__ = ["Vince Reuter", "Kai Sandoval Beckwith"]

__all__ = [
    "ROI_AREA_KEY",
    "ROI_MEAN_INTENSITY_KEY_CAMEL_CASE",  # Only export this (not the snake case one).
    "DifferenceOfGaussiansTransformation",
    "DimensionalityError",
    "RoiCenterKeys",
    "DetectionResult",
    "detect_spots_dog",
    "detect_spots_int",
]
