from dataclasses import dataclass
from icecap.domain.enums import EntityType


@dataclass(frozen=True)
class Entity:
    """Minimal lightweight representation of an object in the game.

    This class serves as the base for all entity types and can be used
    for more detailed querying of the game state.

    """

    guid: int
    """Global unique identifier of the entity.
    
    For players, this changes each time the player enters the world.
    """

    object_address: int
    """Memory address of the object in the game."""

    entity_type: EntityType
    """Entity type of the object.
    
    This is used to differentiate between different types of entities in the game.
    """
