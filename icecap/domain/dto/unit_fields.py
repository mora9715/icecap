from dataclasses import dataclass
from icecap.domain.enums import PlayerClass, Race, Gender, Faction


@dataclass(frozen=True)
class UnitFields:
    level: int
    hit_points: int
    max_hit_points: int
    energy: int
    max_energy: int

    faction: Faction | None = None
    player_class: PlayerClass | None = None
    race: Race | None = None
    gender: Gender | None = None
