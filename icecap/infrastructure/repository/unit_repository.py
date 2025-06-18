from typing import Generator
from icecap.infrastructure.driver import GameDriver
from icecap.domain.models import Unit, Entity
from icecap.domain.enums import EntityType


class UnitRepository:
    """Repository for unit entities."""

    def __init__(self, driver: GameDriver):
        self.driver = driver
        self.object_manager = self.driver.get_object_manager()

    def get_unit_from_entity(self, entity: Entity) -> Unit:
        position = self.object_manager.get_entity_position(entity)
        name = self.driver.name_resolver.resolve_name(entity)

        unit_fields = self.object_manager.get_unit_fields(entity)

        unit = Unit(
            guid=entity.guid,
            object_address=entity.object_address,
            position=position,
            name=name,
            entity_type=EntityType.UNIT,
            unit_fields=unit_fields,
        )
        return unit

    def yield_units(self) -> Generator[Unit, None, None]:
        """Yields all unit entities."""

        for entity in self.object_manager.yield_objects():
            if entity.entity_type != EntityType.UNIT:
                continue

            yield self.get_unit_from_entity(entity)

    def refresh_unit(self, unit: Unit) -> Unit:
        """Refreshes the unit data. Returns a new Unit instance with updated data."""
        object_manager = self.driver.get_object_manager()

        position = object_manager.get_entity_position(unit)
        unit_fields = object_manager.get_unit_fields(unit)

        return Unit(
            guid=unit.guid,
            object_address=unit.object_address,
            position=position,
            name=unit.name,
            entity_type=EntityType.UNIT,
            unit_fields=unit_fields,
        )
