"""Bundle of parameter annotations for use with numpydoc_decorator"""

from typing_extensions import Annotated, Doc

__author__ = "Vince Reuter"


class common_params:  # pylint: disable=invalid-name,missing-class-docstring,too-few-public-methods
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
