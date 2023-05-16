"""
Utility classes intended for use as generic type hints.
"""

from typing import Mapping, TypeVar


# pylint: disable=R0903
class OrderedMapping(Mapping[TypeVar('T'), TypeVar('S')]):
    """
    Marker class representing a dictionary with predictable element order
    (insertion order). Intended for use in type annotations, where a
    collections.OrderedDict with specific element types is expected.
    """
