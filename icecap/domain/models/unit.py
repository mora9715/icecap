from .entity import Entity

from icecap.domain.dto import Position
from icecap.domain.enums import Race, Gender


class Unit(Entity):
    position: Position

    race: Race
    gender: Gender
    level: int
    name: str
    hit_points: int
    max_hit_points: int
    energy: int
    max_energy: int
