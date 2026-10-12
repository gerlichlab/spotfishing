"""Descriptions of parameters that several transformations share, for numpydoc_decorator"""

__author__ = "Vince Reuter"


class common_params:  # noqa: N801
    sigma_narrow = "Standard deviation of the more concentrated of the two smoothing distributions"
    sigma_wide = "Standard deviation of the more diffuse of the two smoothing distributions"
    standardise = "Standardise (mean-0 and spread-1) the image"
