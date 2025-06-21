from .base import CTypeMixin
from dataclasses import dataclass, field
import ctypes


@dataclass(frozen=True, slots=True)
class ObjectPosition(CTypeMixin):
    x: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    y: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    z: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    rotation: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
