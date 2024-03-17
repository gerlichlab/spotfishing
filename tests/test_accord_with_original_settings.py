"""Tests for maintaining accordance with original, fixed settings, as flexibility is added"""

from pathlib import Path

import pandas as pd
import pytest
from helpers import load_image_file
from pandas.testing import assert_frame_equal

from spotfishing import ROI_MEAN_INTENSITY_KEY, detect_spots_dog, detect_spots_int
from spotfishing.detection_result import ROI_CENTER_KEYS

__author__ = "Vince Reuter"
__credits__ = ["Vince Reuter"]


COLUMNS_OF_INTEREST = ROI_CENTER_KEYS + [ROI_MEAN_INTENSITY_KEY]


@pytest.mark.parametrize(
    ["detect", "func_type_name", "threshold", "expand_px"],
    [
        pytest.param(
            detect,
            func_type_name,
            threshold,
            expand_px,
            id=f"{func_type_name}__{threshold}",
        )
        for detect, func_type_name, threshold, expand_px in [
            (detect_spots_dog, "diff_gauss", t, 10) for t in [15, 10]
        ]
        + [(detect_spots_int, "intensity", t, 1) for t in [300, 200]]
    ],
)
@pytest.mark.parametrize("data_name", ["p0_t57_c0", "p13_t57_c0"])
def test_output_is_correct_with_original_settings(
    data_name, detect, func_type_name, threshold, expand_px
):
    exp_name = (
        f"expect__spots_table__{func_type_name}__threshold_{threshold}__{data_name}.csv"
    )
    exp_path = Path(__file__).parent / "data" / "outputs__original_settings" / exp_name
    exp_table = pd.read_csv(exp_path, index_col=0)

    arr_name = f"img__{data_name}__smaller.npy"
    input_image = load_image_file(arr_name)
    obs = detect(input_image=input_image, spot_threshold=threshold, expand_px=expand_px)
    obs_table = obs.table[COLUMNS_OF_INTEREST]

    print("EXPECTED (below):")
    print(exp_table)
    print("OBSERVED (below):")
    print(obs_table)
    
    assert_frame_equal(obs_table, exp_table)
