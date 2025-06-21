from dataclasses import dataclass
from .entity import Entity

from icecap.domain.dto import Position, UnitFields


@dataclass(frozen=True)
class Unit(Entity):
    """Representation of a non-player unit in the game."""

    position: Position
    """The position of the unit in the world."""

    name: str
    """The name of the unit, typically a creature or NPC."""

    unit_fields: UnitFields
    """Fields specific to the unit."""

    def __str__(self) -> str:
        return (
            f"<{self.name}> [{self.unit_fields.race}"
            f" {self.unit_fields.gender} {self.unit_fields.player_class}]"
            f" <Level {self.unit_fields.level}>\n"
            f"[HP: {self.unit_fields.hit_points}/{self.unit_fields.max_hit_points}]"
            f"Position: <{self.position}>"
        )
