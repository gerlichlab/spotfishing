"""Tests that each dataclass's docstring documents its fields

ruff's docstring rules check that a function's docstring documents each of its
parameters, but not that a dataclass's docstring documents each of its fields.
"""

import dataclasses
import importlib
import inspect
import itertools
import pkgutil

import pytest

import spotfishing
import spotfishing_looptrace


def _find_dataclasses() -> list[type]:
    """Each dataclass defined in either package, private modules included."""
    found: list[type] = []
    for package in (spotfishing, spotfishing_looptrace):
        prefix = f"{package.__name__}."
        for info in pkgutil.walk_packages(package.__path__, prefix):
            module = importlib.import_module(info.name)
            found.extend(
                cls
                for _, cls in inspect.getmembers(module, inspect.isclass)
                if dataclasses.is_dataclass(cls) and cls.__module__ == module.__name__
            )
    return found


DATACLASSES = _find_dataclasses()


def _documented_parameters(cls: type) -> list[str]:
    """The names in the Parameters section of a numpydoc docstring, in order."""
    lines = inspect.cleandoc(cls.__doc__ or "").splitlines()
    if "Parameters" not in lines:
        return []
    # Past the section's header and its underline, up to the next section's header.
    section = lines[lines.index("Parameters") + 2 :]
    names: list[str] = []
    for line, following in itertools.pairwise([*section, ""]):
        if following.startswith("---"):
            break
        if line and not line[0].isspace():
            names.append(line.split(" : ")[0])
    return names


def test_the_dataclasses_are_found():
    assert {cls.__name__ for cls in DATACLASSES} >= {
        "DetectionResult",
        "DifferenceOfGaussiansTransformation",
        "DifferenceOfGaussiansSpecificationForLooptrace",
    }


@pytest.mark.parametrize("cls", DATACLASSES, ids=lambda cls: cls.__name__)
def test_a_dataclass_documents_each_field_in_order(cls):
    fields = [field.name for field in dataclasses.fields(cls)]
    assert _documented_parameters(cls) == fields
