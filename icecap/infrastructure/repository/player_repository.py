from typing import Generator
from icecap.infrastructure.driver import GameDriver
from icecap.domain.models import Player, Entity
from icecap.domain.enums import EntityType, Faction, Race, PlayerClass, Gender
from icecap.domain.dto import Position, UnitFields


class PlayerRepository:
    """Repository for player entities.

    This class provides methods to access player entities in the game.
    """

    def __init__(self, driver: GameDriver):
        self.driver = driver
        self.object_manager = self.driver.get_object_manager()

    def get_player_from_entity(self, entity: Entity) -> Player:
        """Extend an Entity object to a Player object.

        This method takes an Entity object and extracts all the necessary information
        to create a Player object.
        """
        position = self.object_manager.get_entity_position(entity)
        name = self.driver.name_resolver.resolve_name(entity)

        unit_fields = self.object_manager.get_unit_fields(entity)
        race = Race(unit_fields.bytes_0_race)

        player = Player(
            guid=entity.guid,
            object_address=entity.object_address,
            position=Position(x=position.x, y=position.y, z=position.z, rotation=position.rotation),
            name=name,
            entity_type=EntityType.PLAYER,
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
        return player

    def yield_players(self) -> Generator[Player, None, None]:
        """Yield all player entities around the local player.

        This method iterates through all objects around the local player and yields
        only those that are of type PLAYER. Each entity is extended to a Player object
        before being yielded.
        """
        for entity in self.object_manager.yield_objects():
            if entity.entity_type != EntityType.PLAYER:
                continue

            yield self.get_player_from_entity(entity)

    def refresh_player(self, player: Player) -> Player:
        """Refresh the player data with the latest information from the game.

        This method retrieves the latest data for a player from the game and
        returns a new Player instance with the updated data. The original Player
        instance is not modified.
        """
        object_manager = self.driver.get_object_manager()

        position = object_manager.get_entity_position(player)
        unit_fields = object_manager.get_unit_fields(player)

        return Player(
            guid=player.guid,
            object_address=player.object_address,
            position=Position(x=position.x, y=position.y, z=position.z, rotation=position.rotation),
            name=player.name,
            entity_type=EntityType.PLAYER,
            unit_fields=UnitFields(
                level=unit_fields.level,
                hit_points=unit_fields.health,
                max_hit_points=unit_fields.max_health,
                faction=player.unit_fields.faction,
                race=player.unit_fields.race,
                player_class=player.unit_fields.player_class,
                gender=player.unit_fields.gender,
            ),
        )

    def get_local_player(self) -> Player:
        """Retrieve the local player entity (the user's character).

        It uses the object manager to get the local player's
        GUID and then searches for the corresponding entity.
        """
        local_player_guid = self.object_manager.get_local_player_guid()

        for entity in self.object_manager.yield_objects():
            if entity.guid == local_player_guid:
                return self.get_player_from_entity(entity)

        raise ValueError("Local player not found in the object manager.")
