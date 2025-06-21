from enum import Enum


class EntityType(Enum):
    """Enumeration of entity types in the game."""

    NONE = 0
    ITEM = 1
    CONTAINER = 2
    UNIT = 3
    PLAYER = 4
    GAME_OBJECT = 5
    DYNAMIC_OBJECT = 6
    CORPSE = 7
