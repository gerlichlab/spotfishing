"""Tests about column names of spot tables"""

import hypothesis as hyp
import numpy as np
import pytest
from spotfishing import detect_spots_dog, detect_spots_int

__author__ = "Vince Reuter"


@pytest.mark.skip("not implemented")
@pytest.mark.parametrize("detect", [detect_spots_dog, detect_spots_int])
def test_spot_table_columns__are_always_as_expected(detect):
    pass
    #spots, img, labs = detect(np.array([], shape=()))


@pytest.mark.skip("not implemented")
@pytest.mark.parametrize("detect", [detect_spots_dog, detect_spots_int])
@pytest.mark.parametrize(["input_image", "expect"], [])
@hyp.given(
    threshold=hyp.strategies.integers(), 
    pixel_expansion=hyp.strategies.integers(), 
)
def test_detectors_give_proper_error_for_bad_input_image(detect, input_image, threshold, pixel_expansion, expect):
    with pytest.raises(type(expect)) as err_ctx:
        detect(input_image=input_image, threshold=threshold, expand_px=pixel_expansion)
    assert err_ctx.value == expect
