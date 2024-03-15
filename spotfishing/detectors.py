"""Different spot detection implementations"""

from typing import Optional, Tuple, Union

import numpy as np
import pandas as pd
from scipy import ndimage as ndi
from skimage.filters import gaussian
from skimage.measure import regionprops_table
from skimage.morphology import ball, remove_small_objects, white_tophat
from skimage.segmentation import expand_labels

__author__ = "Vince Reuter"
__credits__ = ["Vince Reuter", "Kai Sandoval Beckwith"]

__all__ = ["detect_spots_dog", "detec_spots_int"]

Numeric = Union[int, float]

CENTROID_COLUMNS_REMAPPING = {'centroid_weighted-0': 'zc', 'centroid_weighted-1': 'yc', 'centroid_weighted-2': 'xc'}


def detect_spots_dog(*, input_image, spot_threshold: Numeric, expand_px: Optional[int] = 10):
    """Spot detection by difference of Gaussians filter

    Arguments
    ---------
    input_image : ndarray
        3D image in which to detect spots
    spot_threshold : int or float
        Minimum peak value after the DoG transformation to call a peak/spot
    expand_px : int, optional
        Number of pixels by which to expand contiguous subregion, 
        up to point of overlap with neighboring subregion of image
        
    Returns
    -------
    pd.DataFrame, np.ndarray, np.ndarray: 
        The centroids and roi_IDs of the spots found, 
        the image used for spot detection, and 
        numpy array with only sufficiently large regions 
        retained (bigger than threshold number of pixels), 
        and dilated by expansion amount (possibly)
    """
    img = _preprocess_for_difference_of_gaussians(input_image)
    labels, _ = ndi.label(img > spot_threshold)
    spot_props, labels = _build_props_table(labels=labels, input_image=input_image, expand_px=expand_px)
    return spot_props, img, labels


def detect_spots_int(*, input_image, spot_threshold: Numeric, expand_px: Optional[int] = 1):
    """Spot detection by intensity filter

    Arguments
    ---------
    img : ndarray
        Input 3D image
    spot_threshold : NumberLike
        Threshold to use for spots
    expand_px : int
        Number of pixels by which to expand contiguous subregion, 
        up to point of overlap with neighboring subregion of image
        
    Returns
    -------
    pd.DataFrame, np.ndarray, np.ndarray: 
        The centroids and roi_IDs of the spots found, 
        the image used for spot detection, and 
        numpy array with only sufficiently large regions 
        retained (bigger than threshold number of pixels), 
        and dilated by expansion amount (possibly)
    """
    # TODO: enforce that output column names don't vary with code path walked.
    # See: https://github.com/gerlichlab/looptrace/issues/125

    binary = input_image > spot_threshold
    binary = ndi.binary_fill_holes(binary)
    struct = ndi.generate_binary_structure(input_image.ndim, 2)
    labels, num_obj = ndi.label(binary, structure=struct)
    if num_obj > 1:
        labels = remove_small_objects(labels, min_size=5)
    spot_props, labels = _build_props_table(labels=labels, input_image=input_image, expand_px=expand_px)
    return spot_props, input_image, labels


def _build_props_table(*, labels: np.ndarray, input_image: np.ndarray, expand_px: Optional[int]) -> Tuple[pd.DataFrame, np.ndarray]:
    if expand_px:
        labels = expand_labels(labels, expand_px)
    if np.all(labels == 0):
        # No substructures (ROIs) exist.
        spot_props = pd.DataFrame(columns=['label', 'centroid_weighted-0', 'centroid_weighted-1', 'centroid_weighted-2', 'area', 'intensity_mean'])
    else:
        spot_props = regionprops_table(
            label_image=labels, 
            intensity_image=input_image, 
            properties=('label', 'centroid_weighted', 'area', 'intensity_mean'),
            )
        spot_props = pd.DataFrame(spot_props)
    spot_props = spot_props.drop(['label'], axis=1)
    spot_props = spot_props.rename(columns=CENTROID_COLUMNS_REMAPPING)
    spot_props = spot_props.reset_index(drop=True)
    return spot_props, labels


def _preprocess_for_difference_of_gaussians(input_image: np.ndarray) -> np.ndarray:
    img = white_tophat(image=input_image, footprint=ball(2))
    img = gaussian(img, 0.8) - gaussian(img, 1.3)
    img = img / gaussian(input_image, 3)
    img = (img - np.mean(img)) / np.std(img)
    return img
