"""Difference of Gaussians transformation for spot detection with looptrace"""

import json
import math
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Optional, Union

from numpydoc_decorator import doc  # type: ignore[import-untyped]
from skimage.filters import gaussian as gaussian_filter
from skimage.morphology import ball, white_tophat

from spotfishing._transformation_parameters import common_params
from spotfishing._types import Image, ImageEndomorphism
from spotfishing.dog_transform import (
    DifferenceOfGaussiansTransformation,
    PostDifferenceTransformation,
    is_numeric,
)

__author__ = "Vince Reuter"
__credits__ = ["Vince Reuter", "Kai Sandoval Beckwith"]

__all__ = [
    "DifferenceOfGaussiansSpecificationForLooptrace",
    "ORIGINAL_LOOPTRACE_DOG_SPECIFICATION",
]


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
    raises=dict(
        TypeError="If sigma_post_divide is given but isn't a number",
        ValueError="If sigma_post_divide is given but isn't a finite number above 0",
    ),
)
@dataclass(frozen=True, kw_only=True)
class DifferenceOfGaussiansSpecificationForLooptrace:  # pylint: disable=missing-class-docstring
    apply_white_tophat: bool
    sigma_narrow: Numeric
    sigma_wide: Numeric
    sigma_post_divide: Optional[Numeric]
    standardise: bool

    def __post_init__(self) -> None:
        # Checked here, since a bad value would otherwise fail only deep inside detection, or,
        # for 0 or NaN, find no spots, without an error.
        if self.sigma_post_divide is None:
            return
        if not is_numeric(self.sigma_post_divide):
            raise TypeError(
                f"sigma_post_divide must be a number, not {type(self.sigma_post_divide).__name__}: {self.sigma_post_divide!r}"
            )
        if not math.isfinite(self.sigma_post_divide) or self.sigma_post_divide <= 0:
            raise ValueError(
                f"sigma_post_divide must be a finite number above 0, not {self.sigma_post_divide}"
            )

    @property
    def transformation(self) -> "DifferenceOfGaussiansTransformation":
        """Build the DoG transformation from this specification."""
        # https://git.embl.de/grp-ellenberg/looptrace/-/blob/master/looptrace/image_processing_functions.py?ref_type=heads#L252
        pre: Optional[ImageEndomorphism] = (
            partial(white_tophat, footprint=ball(2))
            if self.apply_white_tophat
            else None
        )
        post: Optional[PostDifferenceTransformation] = (
            None
            if self.sigma_post_divide is None
            else partial(div_by_gauss, sigma=self.sigma_post_divide)
        )
        return DifferenceOfGaussiansTransformation(
            pre_diff=pre,
            sigma_narrow=self.sigma_narrow,
            sigma_wide=self.sigma_wide,
            post_diff=post,
            standardise=self.standardise,
        )

    @classmethod
    def from_json_file(
        cls, fp: Path  # pylint: disable=invalid-name
    ) -> "DifferenceOfGaussiansSpecificationForLooptrace":
        """Build an instance from parameters in a JSON file.

        Parameters
        ----------
        fp
            Path to the file to parse for parameters.

        Returns
        -------
        DifferenceOfGaussiansSpecificationForLooptrace
            A newly constructed instance, parameterised according to the data in the
            given config file.
        """
        with open(fp, "r") as handle:
            data = json.load(handle)
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
def div_by_gauss(  # pylint: disable=missing-function-docstring
    *, old_img: Image, new_img: Image, sigma: Numeric
) -> Image:
    # https://git.embl.de/grp-ellenberg/looptrace/-/blob/master/looptrace/image_processing_functions.py?ref_type=heads#L252
    return new_img / gaussian_filter(old_img, sigma)  # type: ignore[no-any-return]


# original parameterisation of the transformation for detection with DoG
ORIGINAL_LOOPTRACE_DOG_SPECIFICATION = DifferenceOfGaussiansSpecificationForLooptrace(
    apply_white_tophat=True,
    sigma_narrow=0.8,
    sigma_wide=1.3,
    sigma_post_divide=3,
    standardise=True,
)
