"""Image processing related to spot detection, but to be run first"""

from dataclasses import dataclass
from typing import Optional, Protocol, Union, get_args

import numpy as np

from ._skimage import gaussian as gaussian_filter
from ._types import FloatImage, Image, ImageEndomorphism, NumpyFloat, NumpyInt

__author__ = "Vince Reuter"
__credits__ = ["Vince Reuter"]

__all__ = ["DifferenceOfGaussiansTransformation"]

Numeric = Union[float, int, NumpyFloat, NumpyInt]


class PostDifferenceTransformation(Protocol):
    def __call__(self, *, old_img: Image, new_img: FloatImage) -> FloatImage: ...


@dataclass(frozen=True, kw_only=True)
class DifferenceOfGaussiansTransformation:
    """Bundle of parameters defining preprocessing for Difference of Gaussians (DoG) detector.

    Chain together a series of operations that to prepare an image for spot
    detection by difference of Gaussians. This includes an optional step to
    do before taking the difference of Gaussian-smoothed images, the spreads
    of the Gaussians to use for the smoothing, and what (if anything) to do
    after subtracting the smoothed versions of the image,.

    Parameters
    ----------
    pre_diff : Callable[[NDArray['PixelValue']], NDArray[PixelValue]] or None
        Transformation to apply to image before taking difference of smoothed
        versions.
    sigma_narrow : float or int or float16 or float32 or float64 or int8 or int16 or int32 or int64
        Standard deviation of the more concentrated of the two smoothing
        distributions.
    sigma_wide : float or int or float16 or float32 or float64 or int8 or int16 or int32 or int64
        Standard deviation of the more diffuse of the two smoothing
        distributions.
    post_diff : PostDifferenceTransformation or None
        What (if anything) to do to the transformed image after difference but
        before standardisation; note that if non-null, this will be fed the
        *original* image as the first argument, and the *transformed image as
        the second argument.
    standardise : bool
        Standardise (mean-0 and spread-1) the image.

    Returns
    -------
    None
        A structure of the same shape as the input, just with all
        transformations applied.

    Raises
    ------
    TypeError
        If either of the standard deviations is non-numeric.
    ValueError
        If the narrower Gaussian's standard deviation isn't less than the
        wider Gaussian's.

    """

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

    def __call__(self, input_image: Image) -> FloatImage:
        """Apply the sequence of transformations in this instance to given image.

        The construction of an instance of this preprocessor parameterises
        several operations that, when run in sequence, comprise a preprocessing
        workflow often used before running spot detection.

        Parameters
        ----------
        input_image : NDArray[PixelValue]
            The image (array of pixel values) to preprocess.

        Returns
        -------
        NDArray[floating[Any]]
            The array of values after transformations' application.

        """
        img = self.pre_diff(input_image) if self.pre_diff is not None else input_image
        img_narrow = gaussian_filter(img, float(self.sigma_narrow))
        img_wide = gaussian_filter(img, float(self.sigma_wide))
        img = img_narrow - img_wide
        if self.post_diff is not None:
            img = self.post_diff(old_img=input_image, new_img=img)
        return (img - np.mean(img)) / np.std(img) if self.standardise else img


def is_numeric(obj: object) -> bool:
    """Test the given object for membership in a numeric type.

    Parameters
    ----------
    obj : object
        Object to test for membership in a numeric type.

    Returns
    -------
    bool

    """
    return isinstance(obj, get_args(Numeric))
