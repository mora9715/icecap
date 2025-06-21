from typing import Generator
from icecap.infrastructure.driver import GameDriver
from icecap.domain.models import Unit, Entity
from icecap.domain.enums import EntityType, Faction, Race, PlayerClass, Gender
from icecap.domain.dto import Position, UnitFields


class UnitRepository:
    """Repository for unit entities.

    This class provides methods to access unit entities in the game.
    """

    def __init__(self, driver: GameDriver):
        self.driver = driver
        self.object_manager = self.driver.get_object_manager()

    def get_unit_from_entity(self, entity: Entity) -> Unit:
        """Extend an Entity object to a Unit object.

        This method takes an Entity object and extracts all the necessary information
        and creates a Unit object from it.
        """
        position = self.object_manager.get_entity_position(entity)
        name = self.driver.name_resolver.resolve_name(entity)

        unit_fields = self.object_manager.get_unit_fields(entity)
        race = Race(unit_fields.bytes_0_race)

        unit = Unit(
            guid=entity.guid,
            object_address=entity.object_address,
            position=Position(x=position.x, y=position.y, z=position.z, rotation=position.rotation),
            name=name,
            entity_type=EntityType.UNIT,
            unit_fields=UnitFields(
                level=unit_fields.level,
                hit_points=unit_fields.health,
                max_hit_points=unit_fields.max_health,
                faction=Faction.from_race(race),
                race=race,
                player_class=PlayerClass(unit_fields.bytes_0_class),
                gender=Gender(unit_fields.bytes_0_gender),
            ),
        )
        return unit

    def yield_units(self) -> Generator[Unit, None, None]:
        """Yield all unit entities around the player.

        This method iterates through all objects around the player and yields
        only those that are of type UNIT. Each entity is extended to a Unit object
        before being yielded.
        """
        for entity in self.object_manager.yield_objects():
            if entity.entity_type != EntityType.UNIT:
                continue

            yield self.get_unit_from_entity(entity)

    def refresh_unit(self, unit: Unit) -> Unit:
        """Refresh the unit data with the latest information from the game.

        This method retrieves the latest data for a unit from the game and
        returns a new Unit instance with the updated data. The original Unit
        instance is not modified.
        """
        object_manager = self.driver.get_object_manager()

        position = object_manager.get_entity_position(unit)
        unit_fields = object_manager.get_unit_fields(unit)

        return Unit(
            guid=unit.guid,
            object_address=unit.object_address,
            position=Position(x=position.x, y=position.y, z=position.z, rotation=position.rotation),
            name=unit.name,
            entity_type=EntityType.UNIT,
            unit_fields=UnitFields(
                level=unit_fields.level,
                hit_points=unit_fields.health,
                max_hit_points=unit_fields.max_health,
                faction=unit.unit_fields.faction,
                race=unit.unit_fields.race,
                player_class=unit.unit_fields.player_class,
                gender=unit.unit_fields.gender,
            ),
        )
