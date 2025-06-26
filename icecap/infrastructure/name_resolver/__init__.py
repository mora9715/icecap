"""The name resolver module."""

from .interface import NameResolver
from .factory import get_name_resolver

__all__ = ["NameResolver", "get_name_resolver"]
