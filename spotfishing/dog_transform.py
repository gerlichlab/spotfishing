"""Image processing related to spot detection, but to be run first"""

from dataclasses import dataclass
from typing import Optional, Protocol, Union

import numpy as np
from numpydoc_decorator import doc  # type: ignore[import-untyped]
from skimage.filters import gaussian as gaussian_filter

from ._transformation_parameters import common_params
from ._types import Image, ImageEndomorphism, NumpyFloat, NumpyInt

__author__ = "Vince Reuter"
__credits__ = ["Vince Reuter"]

__all__ = ["DifferenceOfGaussiansTransformation"]

Numeric = Union[float, int, NumpyFloat, NumpyInt]


class PostDifferenceTransformation(
    Protocol
):  # pylint: disable=too-few-public-methods,missing-class-docstring
    def __call__(self, *, old_img: Image, new_img: Image) -> Image:
        ...


@doc(
    summary="Bundle of parameters defining preprocessing for Difference of Gaussians (DoG) detector",
    extended_summary="""
        Chain together a series of operations that to prepare an image for spot detection by
        difference of Gaussians. This includes an optional step to do before taking the difference 
        of Gaussian-smoothed images, the spreads of the Gaussians to use for the smoothing, and 
        what (if anything) to do after subtracting the smoothed versions of the image,
    """,
    parameters=dict(
        pre_diff="Transformation to apply to image before taking difference of smoothed versions",
        sigma_narrow=common_params.sigma_narrow,
        sigma_wide=common_params.sigma_wide,
        post_diff="What (if anything) to do to the transformed image after difference but before standardisation; note that if non-null, this will be fed the *original* image as the first argument, and the *transformed image as the second argument",
        standardise=common_params.standardise,
    ),
    raises=dict(
        TypeError="If either of the standard deviations is non-numeric.",
        ValueError="If the narrower Gaussian's standard deviation isn't less than the wider Gaussian's.",
    ),
    returns="A structure of the same shape as the input, just with all transformations applied",
)
@dataclass(frozen=True, kw_only=True)
class DifferenceOfGaussiansTransformation:  # pylint: disable=missing-class-docstring
    pre_diff: Optional[ImageEndomorphism]
    sigma_narrow: Numeric
    sigma_wide: Numeric
    post_diff: Optional[PostDifferenceTransformation]
    standardise: bool

    def __post_init__(self) -> None:
        # skimage raises errors for negative sigma, but we raise these.
        if not (is_numeric(self.sigma_narrow) and is_numeric(self.sigma_wide)):
            raise TypeError(
                f"At least one sigma is non-numeric! narrow={self.sigma_narrow} ({type(self.sigma_narrow).__name__}), wide={self.sigma_wide} ({type(self.sigma_wide).__name__}"
            )
        if self.sigma_narrow >= self.sigma_wide:
            raise ValueError(
                f"sigma for narrow Gaussian must be strictly less than sigma for wide Gaussian, but {self.sigma_narrow} >= {self.sigma_wide}"
            )

    @doc(
        summary="Apply the sequence of transformations in this instance to given image.",
        extended_summary="""
        The construction of an instance of this preprocessor parameterises several 
        operations that, when run in sequence, comprise a preprocessing workflow often 
        used before running spot detection.
    """,
        parameters=dict(input_image="The image (array of pixel values) to preprocess"),
        returns="The array of values after transformations' application",
    )
    def __call__(self, input_image: Image) -> Image:
        img = self.pre_diff(input_image) if self.pre_diff is not None else input_image
        img_narrow = gaussian_filter(img, self.sigma_narrow)
        img_wide = gaussian_filter(img, self.sigma_wide)
        img = img_narrow - img_wide
        if self.post_diff is not None:
            img = self.post_diff(old_img=input_image, new_img=img)
        return (img - np.mean(img)) / np.std(img) if self.standardise else img


@doc(
    summary="Test the given object for membership in a numeric type",
    parameters=dict(obj="Object to test for membership in a numeric type"),
)
def is_numeric(obj: object) -> bool:  # pylint: disable=missing-function-docstring
    return isinstance(obj, Numeric)  # type: ignore
