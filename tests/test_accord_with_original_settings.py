"""Tests for maintaining accordance with original, fixed settings, as flexibility is added"""

import pytest

from spotfishing import detect_spots_dog, detect_spots_int
from helpers import load_image_file

__author__ = "Vince Reuter"
__credits__ = ["Vince Reuter"]


@pytest.mark.skip("not implemented")
@pytest.mark.parametrize(
    ["detect", "kwargs"], [(detect_spots_dog, {}), (detect_spots_int, {})]
)
@pytest.mark.parametrize("input_image", [])
def test_output_is_correct_with_original_settings(detect, input_image, kwargs):
    detect(input_image=input_image, **kwargs)
