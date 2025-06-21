from dataclasses import dataclass
from icecap.domain.enums import PlayerClass, Race, Gender, Faction


@dataclass(frozen=True, slots=True)
class UnitFields:
    """Data class representing the fields of a unit.

    This object is shared between players and units.
    """

    level: int
    """The level of the unit."""

    hit_points: int
    """The current hit points of the unit."""

    max_hit_points: int
    """The maximum hit points of the unit."""

    faction: Faction | None = None
    """The faction of the unit, if applicable."""

    player_class: PlayerClass | None = None
    """The class of the player, if applicable."""

    race: Race | None = None
    """The race of the unit, if applicable."""

    gender: Gender | None = None
    """The gender of the unit, if applicable."""
