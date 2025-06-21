from dataclasses import dataclass
from .entity import Entity

from icecap.domain.dto import Position, GameObjectFields


@dataclass(frozen=True)
class GameObject(Entity):
    """Representation of a game object.

    Game objects are entities in the world that can be interacted with,
    manipulated, or observed.

    """

    position: Position
    """The position of the game object in the world."""

    name: str
    """Human-readable name of the game object."""

    game_object_fields: GameObjectFields
    """Fields specific to the game object."""
