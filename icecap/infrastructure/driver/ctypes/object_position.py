from .base import CTypeMixin
from dataclasses import dataclass, field
import ctypes


@dataclass(frozen=True, slots=True)
class ObjectPosition(CTypeMixin):
    y: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    x: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    z: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    _: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    rotation: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
