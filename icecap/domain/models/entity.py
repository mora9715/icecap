from dataclasses import dataclass
from icecap.domain.enums import EntityType


@dataclass(frozen=True)
class Entity:
    """Entity is a minimal representation of an object in the game.

    It can be used for more detailed querying of the game state.
    """

    guid: int
    object_address: int

    entity_type: EntityType
