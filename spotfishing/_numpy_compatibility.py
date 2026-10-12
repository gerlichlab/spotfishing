"""A warning about releases installed with numpy 2 that were built for numpy 1.

spotfishing allows numpy 1 and 2, and releases of pandas, scipy and scikit-image built for numpy 1
only. Such a release fails to import with numpy 2, with an error about binary incompatibility that
doesn't say what to do. pip installs that combination when something else holds one of those
packages back, so the package checks the installed versions first and says which to upgrade.
"""

import importlib.metadata
import re
import warnings

__all__ = ["FIRST_RELEASES_FOR_NUMPY_2", "warn_of_releases_built_for_numpy_1"]

# The first release of each package that was built against numpy 2, and so imports with numpy 1
# and 2 alike. scikit-image 0.23.0 was yanked, for wheels that failed to upload.
FIRST_RELEASES_FOR_NUMPY_2 = {
    "pandas": (2, 2, 2),
    "scipy": (1, 13, 0),
    "scikit-image": (0, 23, 1),
}


def _release(version: str) -> tuple[int, ...]:
    """Give the release numbers a version starts with: (2, 0, 0) for 2.0.0rc1."""
    match = re.match(r"\d+(?:\.\d+)*", version)
    return tuple(int(part) for part in match.group().split(".")) if match else ()


def warn_of_releases_built_for_numpy_1() -> None:
    """Warn if numpy 2 is installed with pandas, scipy or scikit-image built for numpy 1."""
    try:
        numpy = importlib.metadata.version("numpy")
    except importlib.metadata.PackageNotFoundError:
        return
    if _release(numpy) < (2,):
        return
    too_old: list[str] = []
    for package, first in FIRST_RELEASES_FOR_NUMPY_2.items():
        try:
            version = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            continue
        if _release(version) < first:
            too_old.append(f"{package} {version} ({'.'.join(map(str, first))} or later works)")
    if too_old:
        warnings.warn(
            f"numpy {numpy} is installed with releases built for numpy 1, which fail to import "
            f"with numpy 2: {', '.join(too_old)}. Upgrade them, or install numpy below 2.",
            stacklevel=2,
        )
