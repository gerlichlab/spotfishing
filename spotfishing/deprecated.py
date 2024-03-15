from typing import Union

import numpy as np
import pandas as pd
from scipy import ndimage as ndi
from skimage.filters import gaussian
from skimage.measure import regionprops_table
from skimage.morphology import ball, remove_small_objects, white_tophat
from skimage.segmentation import expand_labels

Numeric = Union[int, float]

CENTROID_COLUMNS_REMAPPING = {
    "centroid_weighted-0": "zc",
    "centroid_weighted-1": "yc",
    "centroid_weighted-2": "xc",
}


def detect_spots_dog_old(input_img, spot_threshold: Numeric, expand_px: int = 10):
    """Spot detection by difference of Gaussians filter

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
    # TODO: Do not use hard-coded sigma values (second parameter to gaussian(...)).
    # See: https://github.com/gerlichlab/looptrace/issues/124

    img = white_tophat(image=input_img, footprint=ball(2))
    img = gaussian(img, 0.8) - gaussian(img, 1.3)
    img = img / gaussian(input_img, 3)
    img = (img - np.mean(img)) / np.std(img)
    labels, _ = ndi.label(img > spot_threshold)
    labels = expand_labels(labels, expand_px)

    # Make a DataFrame with the ROI info.
    spot_props = _reindex_to_roi_id(
        pd.DataFrame(
            regionprops_table(
                label_image=labels,
                intensity_image=input_img,
                properties=("label", "centroid_weighted", "intensity_mean"),
            )
        )
        .drop(["label"], axis=1)
        .rename(columns=CENTROID_COLUMNS_REMAPPING)
    )

    return spot_props, img, labels


def detect_spots_int_old(input_img, spot_threshold: Numeric, expand_px: int = 1):
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

    binary = input_img > spot_threshold
    binary = ndi.binary_fill_holes(binary)
    struct = ndi.generate_binary_structure(input_img.ndim, 2)
    labels, n_obj = ndi.label(binary, structure=struct)
    if n_obj > 1:  # Do not need this with area filtering below
        labels = remove_small_objects(labels, min_size=5)
    if expand_px > 0:
        labels = expand_labels(labels, expand_px)
    if np.all(labels == 0):  # No substructures (ROIs) exist after filtering.
        spot_props = pd.DataFrame(
            columns=[
                "label",
                "z_min",
                "y_min",
                "x_min",
                "z_max",
                "y_max",
                "x_max",
                "area",
                "zc",
                "yc",
                "xc",
                "intensity_mean",
            ]
        )
    else:
        spot_props = _reindex_to_roi_id(
            pd.DataFrame(
                regionprops_table(
                    labels,
                    input_img,
                    properties=(
                        "label",
                        "bbox",
                        "area",
                        "centroid_weighted",
                        "intensity_mean",
                    ),
                )
            ).rename(
                columns={
                    **CENTROID_COLUMNS_REMAPPING,
                    "bbox-0": "z_min",
                    "bbox-1": "y_min",
                    "bbox-2": "x_min",
                    "bbox-3": "z_max",
                    "bbox-4": "y_max",
                    "bbox-5": "x_max",
                }
            )
        )

    return spot_props, input_img, labels


def _index_as_roi_id(props_table: pd.DataFrame) -> pd.DataFrame:
    return props_table.rename(columns={"index": "roi_id"})


def _reindex_to_roi_id(props_table: pd.DataFrame) -> pd.DataFrame:
    return _index_as_roi_id(props_table.reset_index(drop=True))
