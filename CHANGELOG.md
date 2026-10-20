# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.4.0] - 2026-10-12

### Added
* `py.typed` markers, so that type checkers use the annotations of `spotfishing` and `spotfishing_looptrace`.
* A warning, when spotfishing is imported, if numpy 2 is installed with a release of pandas, scipy or scikit-image built for numpy 1, which fails to import with it.

### Changed
* Depend on `gertils` v0.7.0.
* Drop support for Python 3.10, and support Python 3.13: spotfishing supports Python 3.11 to 3.13.
* Allow numpy 2 and pandas 2. pandas 1.5.3 had no wheels for Python 3.12 or later.
* Declare `typing-extensions` as a dependency, since spotfishing imports it (#18).
* Type-check with `pyright` instead of `mypy`, and format and lint with `ruff` instead of `black`, `isort` and `pylint` (#14). The checks now cover `spotfishing_looptrace` and its tests too (#9).
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
