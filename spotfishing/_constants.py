"""Constant useful package-wide"""

__author__ = "Vince Reuter"
__credits__ = ["Vince Reuter"]

__all__ = [
    "ROI_AREA_KEY",
    "ROI_CENTROID_KEY",
    "ROI_LABEL_KEY",
    "ROI_MEAN_INTENSITY_KEY",
]


# the key for an ROI's area, coming back from skimage.measure.regionprops_table
ROI_AREA_KEY = "area"

# the key for an ROI's centroid, coming back from skimage.measure.regionprops_table
ROI_CENTROID_KEY = "centroid_weighted"

# the key for an ROI's label, coming back from skimage.measure.regionprops_table
ROI_LABEL_KEY = "label"

# the key for an ROI's average intensity, coming back from skimage.measure.regionprops_table
ROI_MEAN_INTENSITY_KEY = "intensity_mean"
