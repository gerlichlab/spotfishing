"""Narrower error/exception types for this package"""

__author__ = "Vince Reuter"
__credits__ = ["Vince Reuter"]

__all__ = [
    "DimensionalityError",
]


class DimensionalityError(Exception):
    """Error subtype when dimensionality of something isn't as expected"""
