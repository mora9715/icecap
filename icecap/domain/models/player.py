from .entity import Entity

from icecap.domain.dto import Position
from icecap.domain.enums import PlayerClass, Race, Gender


class Player(Entity):
    position: Position
    player_class: PlayerClass
    race: Race
    gender: Gender
    level: int
    name: str
    hit_points: int
    max_hit_points: int
    energy: int
    max_energy: int
