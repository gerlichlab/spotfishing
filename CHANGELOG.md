# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.3.3] - 2025-10-28

### Changed
* Depend on the newest (v0.6.1) version of `gertils`.

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
