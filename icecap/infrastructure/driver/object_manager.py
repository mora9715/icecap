from typing import Generator
from icecap.infrastructure.memory_manager import MemoryManager
from icecap.domain.models import Entity
from icecap.domain.enums import EntityType

from .offsets import (
    FIRST_OBJECT_OFFSET,
    OBJECT_TYPE_OFFSET,
    OBJECT_GUID_OFFSET,
    NEXT_OBJECT_OFFSET,
    LOCAL_PLAYER_GUID_OFFSET,
)


class ObjectManager:
    """Represents the Object Manager in WoW client."""

    def __init__(
        self,
        memory_manager: MemoryManager,
        object_manager_address: int,
        max_objects: int = 1000,
    ):
        self.memory_manager = memory_manager
        self.object_manager_address = object_manager_address

        self.max_objects = max_objects

    def get_local_player_guid(self) -> int:
        """Retrieves the GUID of the local player.
        Uses dynamic address that should be more reliable than static offsets.
        """
        return self.memory_manager.read_ulonglong(
            self.object_manager_address + LOCAL_PLAYER_GUID_OFFSET
        )

    def yield_objects(self) -> Generator[Entity, None, None]:
        """Yields all objects in the Object Manager."""
        checked_objects = 0
        current_object_address = self.memory_manager.read_uint(
            self.object_manager_address + FIRST_OBJECT_OFFSET
        )

        while checked_objects < self.max_objects:
            try:
                object_type = EntityType(
                    self.memory_manager.read_uint(
                        current_object_address + OBJECT_TYPE_OFFSET
                    )
                )
            except Exception:
                break

            object_guid = self.memory_manager.read_ulonglong(
                current_object_address + OBJECT_GUID_OFFSET
            )

            yield Entity(
                guid=object_guid,
                object_address=current_object_address,
                entity_type=object_type,
            )

            checked_objects += 1
            current_object_address = self.memory_manager.read_uint(
                current_object_address + NEXT_OBJECT_OFFSET
            )
