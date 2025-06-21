from .base import CTypeMixin
from dataclasses import dataclass, field
import ctypes


@dataclass(frozen=True, slots=True)
class GameObjectFields(CTypeMixin):
    """Structure representing the fields of a game object."""

    guid: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_ulonglong})
    type: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    entry: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    scale_x: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    padding: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    created_by: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_ulonglong})
    display_id: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    flags: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    parent_rotation_x: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    parent_rotation_y: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    parent_rotation_z: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    parent_rotation_w: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    dynamic_0: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint16})
    dynamic_1: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint16})
    faction: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    level: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    bytes1_state: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint8})
    bytes1_type: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint8})
    bytes1_animation_progress: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint8})
    bytes1_art_kit: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint8})
