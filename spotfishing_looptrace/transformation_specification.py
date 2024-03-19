"""Difference of Gaussians transformation for spot detection with looptrace"""

from dataclasses import dataclass
from functools import partial
import json
from pathlib import Path
from typing import Optional, Union

from numpydoc_decorator import doc  # type: ignore[import-untyped]
from skimage.filters import gaussian as gaussian_filter  # type: ignore[import-untyped]
from skimage.morphology import ball, white_tophat

from spotfishing.dog_transform import (
    DifferenceOfGaussiansTransformation,
    PostDifferenceTransformation,
)
from spotfishing._transformation_parameters import common_params
from spotfishing._types import Image, ImageEndomorphism

__author__ = "Vince Reuter"
__credits__ = ["Vince Reuter", "Kai Sandoval Beckwith"]

__all__ = ["DifferenceOfGaussiansSpecificationForLooptrace"]


Numeric = Union[float, int]


@doc(
    summary="Build an instance with optional white tophat filter as preprocessing, and optional division by a Gaussian blur as postprocessing.",
    parameters=dict(
        apply_white_tophat="Whether to apply a white tophat transformation before taking the difference of the Gaussians",
        sigma_narrow=common_params.sigma_narrow,
        sigma_wide=common_params.sigma_wide,
        sigma_post_divide="The standard deviation of the Gaussian blur to apply after differencing but before potential standardisation",
        standardise=common_params.standardise,
    ),
    returns="A parameterised instance built according to the specification of the arguments provided here",
)
@dataclass(frozen=True, kw_only=True)
class DifferenceOfGaussiansSpecificationForLooptrace:
    apply_white_tophat: bool
    sigma_narrow: Numeric
    sigma_wide: Numeric
    sigma_post_divide: Optional[Numeric]
    standardise: bool

    # @doc(summary="Build the DoG transformation from this specification.")
    @property
    def transformation(self) -> "DifferenceOfGaussiansTransformation":
        # https://git.embl.de/grp-ellenberg/looptrace/-/blob/master/looptrace/image_processing_functions.py?ref_type=heads#L252
        pre: Optional[ImageEndomorphism] = (
            partial(white_tophat, footprint=ball(2))
            if self.apply_white_tophat
            else None
        )
        post: Optional[PostDifferenceTransformation] = (
            None if self.sigma_post_divide is None else partial(div_by_gauss, sigma=3)
        )
        return DifferenceOfGaussiansTransformation(
            pre_diff=pre,
            sigma_narrow=self.sigma_narrow,
            sigma_wide=self.sigma_wide,
            post_diff=post,
            standardise=self.standardise,
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
        return cls(**data)


@doc(
    summary="Divide the image under transformation by a blurred version of the original image.",
    parameters=dict(
        old_img="The original input image to some transformation, to blur and then use as divisor for other image",
        new_img="The image undergoing transformation, to divide by a blurred version of the other image",
        sigma="The standard deviation for the blur to apply",
    ),
    returns="The transformed image",
)
def div_by_gauss(*, old_img: Image, new_img: Image, sigma: Numeric) -> Image:
    # https://git.embl.de/grp-ellenberg/looptrace/-/blob/master/looptrace/image_processing_functions.py?ref_type=heads#L252
    return new_img / gaussian_filter(old_img, sigma)  # type: ignore[no-any-return]
