from typing import Generator
from icecap.infrastructure.driver import GameDriver
from icecap.domain.models import Player, Entity
from icecap.domain.enums import EntityType


class PlayerRepository:
    """Repository for player entities."""

    def __init__(self, driver: GameDriver):
        self.driver = driver
        self.object_manager = self.driver.get_object_manager()

    def get_player_from_entity(self, entity: Entity) -> Player:
        position = self.object_manager.get_entity_position(entity)
        name = self.driver.name_resolver.resolve_name(entity)

        unit_fields = self.object_manager.get_unit_fields(entity)

        player = Player(
            guid=entity.guid,
            object_address=entity.object_address,
            position=position,
            name=name,
            entity_type=EntityType.PLAYER,
            unit_fields=unit_fields,
        )
        return player

    def yield_players(self) -> Generator[Player, None, None]:
        """Yields all player entities."""

        for entity in self.object_manager.yield_objects():
            if entity.entity_type != EntityType.PLAYER:
                continue

            yield self.get_player_from_entity(entity)

    def refresh_player(self, player: Player) -> Player:
        """Refreshes the player data.
        Returns a new Player instance with updated data.
        """
        object_manager = self.driver.get_object_manager()

        position = object_manager.get_entity_position(player)
        unit_fields = object_manager.get_unit_fields(player)

        return Player(
            guid=player.guid,
            object_address=player.object_address,
            position=position,
            name=player.name,
            entity_type=EntityType.PLAYER,
            unit_fields=unit_fields,
        )

    def get_local_player(self) -> Player:
        """Retrieves the local player entity."""
        local_player_guid = self.object_manager.get_local_player_guid()

        for entity in self.object_manager.yield_objects():
            if entity.guid == local_player_guid:
                return self.get_player_from_entity(entity)

        raise ValueError("Local player not found in the object manager.")
