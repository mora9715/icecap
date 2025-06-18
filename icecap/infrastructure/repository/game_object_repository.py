from typing import Generator
from icecap.infrastructure.driver import GameDriver
from icecap.domain.models import GameObject, Entity
from icecap.domain.enums import EntityType


class GameObjectRepository:
    """Repository for game object entities."""

    def __init__(self, driver: GameDriver):
        self.driver = driver
        self.object_manager = self.driver.get_object_manager()

    def get_game_object_from_entity(self, entity: Entity) -> GameObject:
        position = self.object_manager.get_entity_position(entity)
        game_object_fields = self.object_manager.get_game_object_fields(entity)
        name = self.driver.name_resolver.resolve_game_object_name_by_entry_id(
            game_object_fields.entry_id
        )

        game_object = GameObject(
            guid=entity.guid,
            object_address=entity.object_address,
            position=position,
            name=name,
            entity_type=EntityType.GAME_OBJECT,
            game_object_fields=game_object_fields,
        )
        return game_object

    def yield_game_objects(self) -> Generator[GameObject, None, None]:
        """Yields all game object entities."""

        for entity in self.object_manager.yield_objects():
            if entity.entity_type != EntityType.GAME_OBJECT:
                continue

            yield self.get_game_object_from_entity(entity)

    def refresh_game_object(self, unit: GameObject) -> GameObject:
        """
        Refreshes the game object data.
        Returns a new GameObject instance with updated data.
        """
        object_manager = self.driver.get_object_manager()

        position = object_manager.get_entity_position(unit)
        game_object_fields = object_manager.get_game_object_fields(unit)

        return GameObject(
            guid=unit.guid,
            object_address=unit.object_address,
            position=position,
            name=unit.name,
            entity_type=EntityType.GAME_OBJECT,
            game_object_fields=game_object_fields,
        )
