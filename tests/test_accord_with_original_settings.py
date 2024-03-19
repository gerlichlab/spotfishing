"""Tests for maintaining accordance with original, fixed settings, as flexibility is added"""

import importlib.resources as importlib_resources
from functools import partial
from pathlib import Path
from typing import Callable, Optional

import pandas as pd
import pytest
from helpers import ORIGINAL_TRANSFORM, load_image_file
from pandas.testing import assert_frame_equal

import spotfishing
from spotfishing import ROI_MEAN_INTENSITY_KEY, detect_spots_dog, detect_spots_int
from spotfishing.detection_result import ROI_CENTER_KEYS, DetectionResult
from spotfishing.detectors import Image, Numeric
from spotfishing.dog_transform import DifferenceOfGaussiansTransformation

__author__ = "Vince Reuter"
__credits__ = ["Vince Reuter"]


# original pixel expansion setting for detection with DoG
ORIGINAL_DOG_EXPAND_PX = 10

# original pixel expansion setting for detection with simple intensity threshold
ORIGINAL_DOG_EXPAND_PX = 1


def test_original_settings_from_json():
    data_file = (
        importlib_resources.files(spotfishing)
        / "examples"
        / "original__difference_of_gaussians.json"
    )
    obs = DifferenceOfGaussiansTransformation.from_json_file(data_file)
    assert obs == ORIGINAL_TRANSFORM


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
            (
                partial(detect_spots_dog, transform=ORIGINAL_TRANSFORM),
                "diff_gauss",
                t,
                10,
            )
            for t in [15, 10]
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
    obs_table = get_table_result(
        detect=detect, threshold=threshold, expand_px=expand_px, data_name=data_name
    )
    print("EXPECTED (below):")
    print(exp_table)
    print("OBSERVED (below):")
    print(obs_table)
    assert_frame_equal(obs_table, exp_table)


def get_table_result(
    *,
    detect: Callable[[Image, Numeric, Optional[Numeric]], DetectionResult],
    threshold: Numeric,
    expand_px: Optional[Numeric],
    data_name: str,
) -> pd.DataFrame:
    arr_name = f"img__{data_name}__smaller.npy"
    input_image = load_image_file(arr_name)
    obs = detect(input_image, spot_threshold=threshold, expand_px=expand_px)  # type: ignore[call-arg]
    cols = ROI_CENTER_KEYS + [ROI_MEAN_INTENSITY_KEY]
    return obs.table[cols]
