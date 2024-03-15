import os
from pathlib import Path

import numpy as np
import pytest

from spotfishing import detect_spots_dog, detect_spots_int
from spotfishing.deprecated import detect_spots_dog_old, detect_spots_int_old

OLD_PIXEL_EXPANSION_INT = 1
OLD_PIXEL_EXPANSION_DOG = 10


def get_img_data_file(fn: str) -> Path:
    return Path(os.path.dirname(__file__)) / "data" / fn


@pytest.mark.parametrize(
    "data_path",
    [
        get_img_data_file(fn)
        for fn in ("img__p0_t57_c0__smaller.npy", "img__p13_t57_c0__smaller.npy")
    ],
)
@pytest.mark.parametrize(
    ["old_fun", "new_fun", "threshold", "expand_px"],
    [
        (detect_spots_int_old, detect_spots_int, threshold, OLD_PIXEL_EXPANSION_INT)
        for threshold in (500, 300, 100)
    ]
    + [
        (detect_spots_dog_old, detect_spots_dog, threshold, OLD_PIXEL_EXPANSION_DOG)
        for threshold in (20, 15, 10)
    ],
)
def test_eqv(data_path, old_fun, new_fun, threshold, expand_px):
    data = np.load(data_path)
    old_table, _, _ = old_fun(data, threshold)
    new_table, _, _ = new_fun(
        input_image=data, spot_threshold=threshold, expand_px=expand_px
    )
    assert np.all(old_table.index == new_table.index)
    cols = ["zc", "yc", "xc", "area", "intensity_mean"]
    sub_cols = [c for c in cols if c != "area"]  # wasn't in DoG before
    assert list(new_table.columns) == cols
    assert np.all(old_table[sub_cols].to_numpy() == new_table[sub_cols].to_numpy())
