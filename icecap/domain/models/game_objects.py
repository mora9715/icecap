from dataclasses import dataclass
from .entity import Entity

from icecap.domain.dto import Position, GameObjectFields


@dataclass(frozen=True)
class GameObject(Entity):
    position: Position

    name: str
    game_object_fields: GameObjectFields
