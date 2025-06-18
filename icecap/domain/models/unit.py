from dataclasses import dataclass
from .entity import Entity

from icecap.domain.dto import Position, UnitFields


@dataclass(frozen=True)
class Unit(Entity):
    position: Position

    name: str
    unit_fields: UnitFields

    def __str__(self) -> str:
        return (
            f"<{self.name}> [{self.unit_fields.race}"
            f" {self.unit_fields.gender} {self.unit_fields.player_class}]"
            f" <Level {self.unit_fields.level}>\n"
            f"[HP: {self.unit_fields.hit_points}/{self.unit_fields.max_hit_points}]"
            f" <Energy: {self.unit_fields.energy}/{self.unit_fields.max_energy}>\n"
            f"Position: <{self.position}>"
        )
