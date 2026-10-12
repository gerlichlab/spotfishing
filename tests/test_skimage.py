"""Tests for the typed scikit-image functions"""

import numpy as np
import pytest

from spotfishing._skimage import remove_small_objects


@pytest.mark.filterwarnings("error::FutureWarning")
def test_remove_small_objects_removes_the_objects_of_max_size_or_smaller():
    """Before scikit-image 0.26 as after, and without its warning about min_size."""
    labels = np.zeros((1, 3, 10), dtype=np.int32)
    labels[0, 0, :5] = 1  # 5 pixels, exactly max_size
    labels[0, 2, :6] = 2  # 6 pixels, more than max_size
    assert set(np.unique(remove_small_objects(labels, max_size=5))) == {0, 2}
