"""Tests for the warning about releases built for numpy 1"""

import importlib.metadata
import warnings

import pytest

from spotfishing import _numpy_compatibility


def _installed(versions):
    """Stand in for importlib.metadata.version, with the given packages installed."""

    def version(package):
        if package not in versions:
            raise importlib.metadata.PackageNotFoundError(package)
        return versions[package]

    return version


def test_numpy_2_with_a_pandas_built_for_numpy_1_warns_naming_it(monkeypatch):
    monkeypatch.setattr(
        importlib.metadata,
        "version",
        _installed({"numpy": "2.4.6", "pandas": "1.5.3", "scipy": "1.17.1"}),
    )
    with pytest.warns(UserWarning, match=r"pandas 1\.5\.3 \(2\.2\.2 or later works\)"):
        _numpy_compatibility.warn_of_releases_built_for_numpy_1()


@pytest.mark.parametrize(
    "versions",
    [
        # Releases for numpy 1, with numpy 1, as in looptrace.
        {"numpy": "1.24.4", "pandas": "1.5.3", "scipy": "1.10.1", "scikit-image": "0.20.0"},
        # The first releases built for numpy 2, with its first release candidate.
        {"numpy": "2.0.0rc1", "pandas": "2.2.2", "scipy": "1.13.0", "scikit-image": "0.23.1"},
        # Without numpy, there is nothing to check.
        {"pandas": "1.5.3"},
    ],
)
def test_no_warning_without_a_release_built_for_numpy_1_and_numpy_2(monkeypatch, versions):
    monkeypatch.setattr(importlib.metadata, "version", _installed(versions))
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        _numpy_compatibility.warn_of_releases_built_for_numpy_1()
