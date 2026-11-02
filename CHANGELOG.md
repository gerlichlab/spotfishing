# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
* Depend on `gertils` v0.8.0, which requires zarr 3. spotfishing reads no zarr data itself.
See [looptrace issue 579](https://github.com/gerlichlab/looptrace/issues/579), which moves looptrace to zarr 3.
* The lock has dask 2026.8.0, as gertils v0.8.0's does: the dask it had, 2023.12.1, can't read zarr 3 stores. It also has numpy 2.5.4 and scipy 1.18.1, which it held back to releases that install on Python 3.11.
* ruff 0.7.4 -> 0.17.3 and pyright 1.1.411 -> 1.1.414, the newest releases, as in looptrace, gertils and the napari plugins. The configuration names the rules that ruff renamed (`TC002`, `TC003`), no longer names those it removed (`ANN101`, `ANN102`), and ignores two that every rule now brings in: a copyright notice in each file (`CPY001`), as the LICENSE covers them all, and `X | None` for `Optional[X]` (`UP045`), which ruff split out of `UP007`, already ignored. In the tests, a test's count of positional parameters (`PLR0917`) is ignored as their count of parameters already was, since pytest passes them by name. ruff sorts four `__all__` lists, one `noqa` that hid nothing goes, and the generic functions of `spotfishing._skimage` declare their own type parameters. pyright 1.1.414 finds nothing new.

### Removed
* Support for Python 3.11. spotfishing requires Python 3.12 or 3.13, as gertils v0.8.0 does, and the newest releases of numpy, zarr and numcodecs. looptrace already requires Python 3.12. CI, the nox sessions and the Nix shell use Python 3.12 and 3.13, and ruff targets Python 3.12: `Record` in `spotfishing.roi_tools` is a `type` alias.

## [v0.4.1] - 2026-10-29

### Changed
* Allow pandas 3. The tests pass on Python 3.12 with pandas 3.0.6 and 3.1.0, numpy 2.5.4, scipy 1.18.1 and scikit-image 0.26.0, with future and deprecation warnings raised as errors. The lock has pandas 3.1, so CI tests it on Python 3.11 to 3.13.

### Fixed
* `detect_spots_dog` and `detect_spots_int` no longer pass `inplace` to `DataFrame.rename`, which pandas 3.1 deprecates: with pandas 3.1, every detection warned with a `Pandas4Warning`, and pandas 4 removes the keyword.

## [v0.4.0] - 2026-10-12

### Added
* `py.typed` markers, so that type checkers use the annotations of `spotfishing` and `spotfishing_looptrace`.
* A warning, when spotfishing is imported, if numpy 2 is installed with a release of pandas, scipy or scikit-image built for numpy 1, which fails to import with it. It shows only when spotfishing is imported before them; otherwise their own import error comes first.

### Changed
* Depend on `gertils` v0.7.0.
* Drop support for Python 3.10, and support Python 3.13: spotfishing supports Python 3.11 to 3.13.
* Allow numpy 2 and pandas 2. pandas 1.5.3 had no wheels for Python 3.12 or later.
* Declare `typing-extensions` as a dependency, since spotfishing imports it (#18).
* Type-check with `pyright` instead of `mypy`, and format and lint with `ruff` instead of `black`, `isort` and `pylint` (#14). The checks now cover `spotfishing_looptrace` and its tests too (#9). The line length stays 88, ruff's default, and ruff and pyright are at the versions looptrace locks, 0.7.4 and 1.1.411, as in the other repositories behind looptrace (#24).
* The Nix shell uses nixpkgs 26.05, with Poetry 2 (#16).
* `DifferenceOfGaussiansSpecificationForLooptrace` refuses a `sigma_post_divide` that isn't a finite number above 0, or that is a bool, which used to mean 3 like any value but `null`.
* `DifferenceOfGaussiansSpecificationForLooptrace.from_json_file` reads the file as UTF-8.
* When `detect_spots_int` finds more than one object, it removes those of 5 pixels or fewer on every scikit-image, the rule looptrace has used since scikit-image 0.26 (#21). Before 0.26 it removed only those smaller than 5 pixels, so there it now finds fewer spots. On 0.26 and later its results are unchanged, without the `FutureWarning` that 0.26 raised on every call.

### Fixed
* `DifferenceOfGaussiansSpecificationForLooptrace` divides by a blur with its `sigma_post_divide`, where it always used 3 (#17). The original looptrace settings use 3, so their results are unchanged; a specification with another value now gives different results.
* The error for a `DetectionResult` whose image isn't 3D gives the image's number of dimensions, where it printed `{self.image.ndim}` (#19).
* The detectors' documentation names the errors both raise for a bad input image, and `detect_spots_int`'s no longer documents an error about a `transform` parameter it doesn't have (#20).
* The documentation of the difference-of-Gaussians transformation and its looptrace specification describes `sigma_narrow`, `sigma_wide` and `standardise`, where those descriptions were empty.

## [v0.3.3] - 2025-10-29

### Changed
* Depend on the newest (v0.6.1) version of `gertils`.
* Formatting changes for CI

## [v0.3.2] - 2025-06-27

### Changed
* Allow more aggressive advancement of the version of `scikit-image` being used, for compatibility with packages which consume this one.

## [v0.3.1] - 2025-04-02

### Changed
* Bump `gertils` dependency up to v0.6.0

## [v0.3.0] - 2024-11-21

### Added
* `get_centroid_from_record` to get the coordinates of the center of a spot ROI from a detection result record

## [v0.2.1] - 2024-11-21

### Changed
* Allow Python 3.12.

## [v0.2.0] - 2024-10-03

### Changed
* Renaming `mean_intensity` to `meanIntensity` right away after detection, before writing to disk.

## [v0.1.0] - 2024-04-18
 
### Added
* This package, first release
