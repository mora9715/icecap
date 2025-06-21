from dataclasses import dataclass
from .entity import Entity
from icecap.domain.dto import Position, UnitFields


@dataclass(frozen=True)
class Player(Entity):
    """Representation of a player in the game."""

    position: Position
    """The position of the player in the world."""

    name: str
    """The name of the player."""

    unit_fields: UnitFields
    """Fields specific to the player."""

    def __str__(self) -> str:
        return (
            f"<{self.name}> [{self.unit_fields.race}"
            f" {self.unit_fields.player_class}] <Level {self.unit_fields.level}>\n"
            f"[HP: {self.unit_fields.hit_points}/{self.unit_fields.max_hit_points}]"
            f"Position: <{self.position}>"
        )

    def is_enemy(self, other: "Player") -> bool:
        """Determines if the other player is an enemy."""
        return self.unit_fields.faction != other.unit_fields.faction
