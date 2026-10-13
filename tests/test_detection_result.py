"""Tests for the wrapper of a spot detection result"""

import numpy as np
import pandas as pd
import pytest

from spotfishing.detection_result import (
    DETECTION_RESULT_TABLE_COLUMNS,
    DetectionResult,
    IllegalDetectionResult,
)


def test_an_image_that_is_not_3d_is_refused_naming_its_dimensions() -> None:
    """See: https://github.com/gerlichlab/spotfishing/issues/19"""
    table = pd.DataFrame(columns=DETECTION_RESULT_TABLE_COLUMNS)
    with pytest.raises(IllegalDetectionResult, match=r"2-dimensional \(not 3!\)"):
        DetectionResult(
            table=table,
            image=np.zeros((2, 2), dtype=np.uint16),
            labels=np.zeros((2, 2), dtype=np.int32),
        )
