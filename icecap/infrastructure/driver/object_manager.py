"""The object manager."""

from typing import Generator
from icecap.infrastructure.memory_manager import MemoryManager
from icecap.domain.models import Entity
from icecap.domain.enums import EntityType
from icecap.infrastructure.driver.ctypes import (
    ObjectPosition,
    UnitFields,
    GameObjectFields,
)

from .offsets import (
    FIRST_OBJECT_OFFSET,
    OBJECT_TYPE_OFFSET,
    OBJECT_GUID_OFFSET,
    NEXT_OBJECT_OFFSET,
    LOCAL_PLAYER_GUID_OFFSET,
    OBJECT_X_POSITION_OFFSET,
    OBJECT_FIELDS_OFFSET,
)


class ObjectManager:
    """Represents the Object Manager in the game client.

    The Object Manager is responsible for keeping track of all game objects,
    units, and players in the game world.
    This class provides methods to access and interact with these
    entities through memory reading operations.

    """

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
        """Retrieve the GUID of the local player using a dynamic address.

        This method uses a dynamic address that should be more reliable than static offsets.
        It reads the local player GUID directly from the object manager.
        """
        return self.memory_manager.read_ulonglong(
            self.object_manager_address + LOCAL_PLAYER_GUID_OFFSET
        )

    def yield_objects(self) -> Generator[Entity, None, None]:
        """Yield all objects in the Object Manager.

        This method iterates through the linked list of objects in the Object Manager
        and yields each one as an Entity object.
        """
        checked_objects = 0
        current_object_address = self.memory_manager.read_uint(
            self.object_manager_address + FIRST_OBJECT_OFFSET
        )

        while checked_objects < self.max_objects:
            try:
                object_type = EntityType(
                    self.memory_manager.read_uint(current_object_address + OBJECT_TYPE_OFFSET)
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

    def get_entity_position(self, entity: Entity) -> ObjectPosition:
        """Retrieve the position of an entity in the game world.

        This method reads the entity's position data from memory and returns it
        as an ObjectPosition object containing x, y, z coordinates and rotation.
        """
        object_position = self.memory_manager.read_ctype_dataclass(
            entity.object_address + OBJECT_X_POSITION_OFFSET, ObjectPosition
        )

        return object_position

    def get_unit_fields(self, entity: Entity) -> UnitFields:
        """Retrieve the unit fields of an entity.

        This method reads the unit's field data from memory and returns it as a
        UnitFields object that corresponds to the C struct definition.
        """
        unit_fields_address = self.memory_manager.read_uint(
            entity.object_address + OBJECT_FIELDS_OFFSET
        )

        unit_fields = self.memory_manager.read_ctype_dataclass(unit_fields_address, UnitFields)

        return unit_fields

    def get_game_object_fields(self, entity: Entity) -> GameObjectFields:
        """Retrieve the game object fields of a game object entity.

        This method reads the game object's field data from memory and returns it as a
        GameObjectFields object that corresponds to the C struct definition.
        """
        fields_address = self.memory_manager.read_uint(entity.object_address + OBJECT_FIELDS_OFFSET)

        game_object_fields = self.memory_manager.read_ctype_dataclass(
            fields_address, GameObjectFields
        )

        return game_object_fields
