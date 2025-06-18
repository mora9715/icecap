from dataclasses import dataclass
from .entity import Entity

from icecap.domain.dto import Position, UnitFields


@dataclass(frozen=True)
class Player(Entity):
    """Player represents a player entity in the game."""

    position: Position
    name: str

    unit_fields: UnitFields

    def __str__(self) -> str:
        return (
            f"<{self.name}> [{self.unit_fields.race}"
            f" {self.unit_fields.player_class}] <Level {self.unit_fields.level}>\n"
            f"[HP: {self.unit_fields.hit_points}/{self.unit_fields.max_hit_points}]"
            f" <Energy: {self.unit_fields.energy}/{self.unit_fields.max_energy}>\n"
            f"Position: <{self.position}>"
        )

    def is_enemy(self, other: "Player") -> bool:
        """Determines if the other player is an enemy."""
        return self.unit_fields.faction != other.unit_fields.faction
