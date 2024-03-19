"""Image processing related to spot detection, but to be run first"""

import json
from dataclasses import dataclass
from operator import itemgetter
from pathlib import Path
from typing import Callable, Dict, Optional, Union

import numpy as np
import numpy.typing as npt
from numpydoc_decorator import doc  # type: ignore[import-untyped]
from skimage.filters import gaussian as gaussian_filter  # type: ignore[import-untyped]
from skimage.morphology import ball, white_tophat
from typing_extensions import Annotated, Doc

from ._numeric_types import NumpyFloat, NumpyInt, PixelValue

__author__ = "Vince Reuter"
__credits__ = ["Vince Reuter"]

__all__ = ["DifferenceOfGaussiansTransformation"]

Image = npt.NDArray[PixelValue]
Numeric = Union[float, int, NumpyFloat, NumpyInt]


@doc(
    summary="Function that, when parameterised, takes an image and gives another image of same shape.",
    parameters=dict(
        _full_func="The function to which to pass an input image and parameters",
        parameters="Parameters to pass to `_full_func`, besides the input image argument",
    ),
)
@dataclass(eq=False)
class ImageEndomorphism:  # type: ignore[misc]
    _full_func: Callable[..., Image]  # type: ignore[misc]
    parameters: Dict[str, object]

    def __call__(self, img: Image) -> Image:
        return self._full_func(img, **self.parameters)

    def __eq__(self, other: "ImageEndomorphism") -> bool:  # type: ignore[override]
        # Handle fact that a parameter may be an array (e.g. ball(2) for white_tophat).
        if type(other) is not type(self) or self._full_func != other._full_func:
            return False
        kvs_this = sorted(self.parameters.items(), key=itemgetter(0))
        kvs_that = sorted(other.parameters.items(), key=itemgetter(0))
        return all(
            k1 == k2
            and (
                np.array_equal(v1, v2)  # type: ignore[arg-type]
                if self._is_arr(v1) and self._is_arr(v2)
                else v1 == v2
            )
            for (k1, v1), (k2, v2) in zip(kvs_this, kvs_that)
        )

    @staticmethod
    def _is_arr(obj: object) -> bool:
        return isinstance(obj, np.ndarray)


@doc(
    summary="Function that, when parameterised, takes an two images and gives an image of same shape as the second.",
    parameters=dict(
        _full_func="The function to which to pass an input images and parameters",
        parameters="Parameters to pass to `_full_func`, besides the input image arguments",
    ),
)
@dataclass
class ImageMorphism21:  # type: ignore[misc]
    _full_func: Callable[..., Image]  # type: ignore[misc]
    parameters: Dict[str, object]

    def __call__(self, *, old_img: Image, new_img: Image) -> Image:
        return self._full_func(old_img=old_img, new_img=new_img, **self.parameters)


class common_params:
    sigma_narrow = Annotated[
        str,
        Doc(
            "Standard deviation of the more concentrated of the two smoothing distributions"
        ),
    ]
    sigma_wide = Annotated[
        str,
        Doc(
            "Standard deviation of the more diffuse of the two smoothing distributions"
        ),
    ]
    standardise = Annotated[str, Doc("Standardise (mean-0 and spread-1) the image")]


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
class DifferenceOfGaussiansTransformation:
    pre_diff: Optional[ImageEndomorphism]
    sigma_narrow: Numeric
    sigma_wide: Numeric
    post_diff: Optional[ImageMorphism21]
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
        img = (
            self.post_diff(old_img=input_image, new_img=img)
            if self.post_diff is not None
            else img
        )
        return (img - np.mean(img)) / np.std(img) if self.standardise else img  # type: ignore[no-any-return]

    # @doc(
    #     summary="Build an instance with optional white tophat filter as preprocessing, and optional division by a Gaussian blur as postprocessing.",
    #     parameters=dict(
    #         apply_white_tophat="Whether to apply a white tophat transformation before taking the difference of the Gaussians",
    #         sigma_narrow=common_params.sigma_narrow,
    #         sigma_wide=common_params.sigma_wide,
    #         sigma_post_divide="The standard deviation of the Gaussian blur to apply after differencing but before potential standardisation",
    #         standardise=common_params.standardise,
    #     ),
    #     returns="A parameterised instance built according to the specification of the arguments provided here",
    # )
    @classmethod
    def build(
        cls,
        *,
        apply_white_tophat: bool,
        sigma_narrow: Numeric,
        sigma_wide: Numeric,
        sigma_post_divide: Optional[Numeric],
        standardise: bool,
    ) -> "DifferenceOfGaussiansTransformation":
        # https://git.embl.de/grp-ellenberg/looptrace/-/blob/master/looptrace/image_processing_functions.py?ref_type=heads#L252
        return cls(
            pre_diff=ImageEndomorphism(white_tophat, dict(footprint=ball(2)))
            if apply_white_tophat
            else None,
            sigma_narrow=sigma_narrow,
            sigma_wide=sigma_wide,
            post_diff=None
            if sigma_post_divide is None
            else ImageMorphism21(div_by_gauss, dict(sigma=3)),
            standardise=standardise,
        )

    # @doc(
    #     summary="Build an instance from parameters in a JSON file.",
    #     parameters=dict(
    #         fp="Path to the file to parse for parameters",
    #     ),
    #     returns="A newly constructed instance, parameterised according to the data in the given config file",
    #     see_also=":meth:`DifferenceOfGaussiansTransformation.build`",
    # )
    @classmethod
    def from_json_file(cls, fp: Path) -> "DifferenceOfGaussiansTransformation":
        with open(fp, "r") as fh:
            data = json.load(fh)
        return cls.build(**data)


def div_by_gauss(*, old_img: Image, new_img: Image, sigma: Numeric) -> Image:
    # https://git.embl.de/grp-ellenberg/looptrace/-/blob/master/looptrace/image_processing_functions.py?ref_type=heads#L252
    return new_img / gaussian_filter(old_img, sigma)  # type: ignore[no-any-return]


@doc(
    summary="Test the given object for membership in a numeric type",
    parameters=dict(obj="Object to test for membership in a numeric type"),
)
def is_numeric(obj: object) -> bool:
    return isinstance(obj, Numeric)  # type: ignore
