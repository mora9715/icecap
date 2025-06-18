from typing import Generator
from icecap.infrastructure.memory_manager import MemoryManager
from icecap.domain.models import Entity
from icecap.domain.enums import EntityType, Race, PlayerClass, Gender, Faction
from icecap.domain.dto import Position, UnitFields, GameObjectFields

from .offsets import (
    FIRST_OBJECT_OFFSET,
    OBJECT_TYPE_OFFSET,
    OBJECT_GUID_OFFSET,
    NEXT_OBJECT_OFFSET,
    LOCAL_PLAYER_GUID_OFFSET,
    OBJECT_ROTATION_OFFSET,
    OBJECT_X_POSITION_OFFSET,
    OBJECT_Y_POSITION_OFFSET,
    OBJECT_Z_POSITION_OFFSET,
    OBJECT_LEVEL_OFFSET,
    OBJECT_HIT_POINTS_OFFSET,
    OBJECT_ENERGY_OFFSET,
    OBJECT_MAX_HIT_POINTS_OFFSET,
    OBJECT_MAX_ENERGY_OFFSET,
    OBJECT_UNIT_BYTE_0_OFFSET,
    OBJECT_FIELDS_OFFSET,
    OBJECT_CREATED_BY_OFFSET,
    OBJECT_DISPLAY_ID_OFFSET,
    OBJECT_ENTRY_ID_OFFSET,
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

    def get_entity_position(self, entity: Entity) -> Position:
        """Retrieves the position of an entity."""
        x = self.memory_manager.read_float(
            entity.object_address + OBJECT_X_POSITION_OFFSET
        )
        y = self.memory_manager.read_float(
            entity.object_address + OBJECT_Y_POSITION_OFFSET
        )
        z = self.memory_manager.read_float(
            entity.object_address + OBJECT_Z_POSITION_OFFSET
        )
        rotation = self.memory_manager.read_float(
            entity.object_address + OBJECT_ROTATION_OFFSET
        )

        return Position(x=x, y=y, z=z, rotation=rotation)

    def get_unit_fields(self, entity: Entity) -> UnitFields:
        """Retrieves the unit fields of an entity."""
        # TODO: Check if unit fields are available for all entities.
        unit_fields_address = self.memory_manager.read_uint(
            entity.object_address + OBJECT_FIELDS_OFFSET
        )

        level = self.memory_manager.read_uint(unit_fields_address + OBJECT_LEVEL_OFFSET)
        hit_points = self.memory_manager.read_uint(
            unit_fields_address + OBJECT_HIT_POINTS_OFFSET
        )
        energy = self.memory_manager.read_uint(
            unit_fields_address + OBJECT_ENERGY_OFFSET
        )
        max_hit_points = self.memory_manager.read_uint(
            unit_fields_address + OBJECT_MAX_HIT_POINTS_OFFSET
        )
        max_energy = self.memory_manager.read_uint(
            unit_fields_address + OBJECT_MAX_ENERGY_OFFSET
        )

        packed_unit_details = self.memory_manager.read_uint(
            unit_fields_address + OBJECT_UNIT_BYTE_0_OFFSET
        )

        race = Race(packed_unit_details & 0xFF)
        player_class = PlayerClass((packed_unit_details >> 8) & 0xFF)
        gender = Gender((packed_unit_details >> 16) & 0xFF)
        _ = (packed_unit_details >> 24) & 0xFF

        return UnitFields(
            level=level,
            hit_points=hit_points,
            energy=energy,
            max_hit_points=max_hit_points,
            max_energy=max_energy,
            player_class=player_class,
            race=race,
            gender=gender,
            faction=Faction.from_race(race),
        )

    def get_game_object_fields(self, entity: Entity) -> GameObjectFields:
        """Retrieves the game object fields of a game object."""

        fields_address = self.memory_manager.read_uint(
            entity.object_address + OBJECT_FIELDS_OFFSET
        )

        created_by = self.memory_manager.read_ulonglong(
            fields_address + OBJECT_CREATED_BY_OFFSET
        )
        display_id = self.memory_manager.read_uint(
            fields_address + OBJECT_DISPLAY_ID_OFFSET
        )
        entry_id = self.memory_manager.read_uint(
            fields_address + OBJECT_ENTRY_ID_OFFSET
        )
        return GameObjectFields(
            owner_guid=created_by, display_id=display_id, entry_id=entry_id
        )
