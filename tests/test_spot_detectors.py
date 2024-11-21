"""Tests about column names of spot tables"""

from functools import partial

import hypothesis as hyp
import numpy as np
import numpy.testing as np_test
import pandas as pd
import pytest
from helpers import load_image_file

from spotfishing import DimensionalityError, detect_spots_dog, detect_spots_int
from spotfishing.detection_result import DETECTION_RESULT_TABLE_COLUMNS
from spotfishing_looptrace import ORIGINAL_LOOPTRACE_DOG_SPECIFICATION

__author__ = "Vince Reuter"
__credits__ = ["Vince Reuter"]


# Generators for dummy numpy arrays to use as input in test cases
gen_small_image_side_length = hyp.strategies.integers(min_value=0, max_value=10)
gen_dims_for_small_image = hyp.strategies.tuples(
    gen_small_image_side_length,
    gen_small_image_side_length,
    gen_small_image_side_length,
)
gen_empty_small_image = gen_dims_for_small_image.map(lambda dims: np.empty(shape=dims))


# detection function, threshold setting, and pixel expansion setting
BASE_INTENSITY_BUNDLE = (detect_spots_int, 300, 1)
BASE_DOG_BUNDLE = (
    partial(
        detect_spots_dog, transform=ORIGINAL_LOOPTRACE_DOG_SPECIFICATION.transformation
    ),
    15,
    10,
)


# @pytest.mark.parametrize("detect", [detect_spots_dog, detect_spots_int])
@pytest.mark.parametrize(
    ["detect", "threshold", "pixel_expansion"], [BASE_DOG_BUNDLE, BASE_INTENSITY_BUNDLE]
)
@pytest.mark.parametrize(
    "input_image",
    [load_image_file("img__p0_t57_c0__smaller.npy"), np.empty(shape=(10, 10, 10))],
)
def test_spot_table_columns__are_always_as_expected(
    detect,
    threshold,
    pixel_expansion,
    input_image,
):
    result = detect(input_image, spot_threshold=threshold, expand_px=pixel_expansion)
    observed_columns = list(result.table.columns)
    assert isinstance(result.table, pd.DataFrame)
    assert observed_columns == DETECTION_RESULT_TABLE_COLUMNS


@pytest.mark.parametrize(
    "input_image",
    [load_image_file("img__p0_t57_c0__smaller.npy"), np.empty(shape=(10, 10, 10))],
)
def test_simple_intensity_detector_result_always_contains_original_image(input_image):
    detect, threshold, pixel_expansion = BASE_INTENSITY_BUNDLE
    result = detect(input_image, spot_threshold=threshold, expand_px=pixel_expansion)
    np_test.assert_allclose(result.image, input_image)


@pytest.mark.parametrize(
    "detect",
    [
        partial(
            detect_spots_dog,
            transform=ORIGINAL_LOOPTRACE_DOG_SPECIFICATION.transformation,
        ),
        detect_spots_int,
    ],
)
@pytest.mark.parametrize(
    ["input_image", "expected_error_type", "expected_message"],
    [
        # bad input image type cases
        (
            obj,
            TypeError,
            f"Expected numpy array for input image but got {type(obj).__name__}",
        )
        for obj in [[], pd.DataFrame()]
    ]
    + [
        # bad input image dimension cases
        (
            obj,
            DimensionalityError,
            f"Expected 3D input image but got {obj.ndim}-dimensional",
        )
        for obj in [
            np.empty(shape=tuple()),
            np.ones(10),
            np.zeros(4).reshape(2, 2),
            np.zeros(36).reshape(2, 3, 3, 2),
        ]
    ],
)
@hyp.given(
    threshold=hyp.strategies.integers(min_value=0, max_value=10000),
    pixel_expansion=hyp.strategies.integers(min_value=0, max_value=100),
)
def test_detectors_give_proper_error_for_bad_input_image(
    detect,
    input_image,
    threshold,
    pixel_expansion,
    expected_error_type,
    expected_message,
):
    with pytest.raises(expected_error_type) as err_ctx:
        detect(input_image, spot_threshold=threshold, expand_px=pixel_expansion)
    assert str(err_ctx.value) == expected_message
