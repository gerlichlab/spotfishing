"""Tests for getting a region's centroid from a record"""

import numpy as np
import pytest
from gertils.geometry import ImagePoint3D

from spotfishing import detect_spots_int
from spotfishing.roi_tools import get_centroid_from_record


def test_centroid_from_a_mapping():
    rec = {"zc": 1.5, "yc": 2.0, "xc": 3.25}
    assert get_centroid_from_record(rec) == ImagePoint3D(z=1.5, y=2.0, x=3.25)


def test_centroid_from_each_row_of_a_detection_table():
    """As looptrace takes them: one row at a time of a table of detected spots.

    gertils checks the coordinates' types when the point is built, so this also checks
    that the table's coordinates are of a type gertils accepts.
    """
    img = np.zeros((3, 10, 10), dtype=np.uint16)
    img[1, 1:4, 1:4] = 500
    img[1, 6:9, 5:8] = 500
    table = detect_spots_int(img, spot_threshold=100, expand_px=0).table
    points = [get_centroid_from_record(row) for _, row in table.iterrows()]
    assert points == [
        ImagePoint3D(z=1.0, y=2.0, x=2.0),
        ImagePoint3D(z=1.0, y=7.0, x=6.0),
    ]


def test_a_record_without_a_coordinate_is_refused():
    with pytest.raises(KeyError):
        get_centroid_from_record({"zc": 1.0, "yc": 2.0})
