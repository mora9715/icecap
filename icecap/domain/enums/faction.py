from enum import Enum

from icecap.domain.enums.race import Race


class Faction(Enum):
    """Enumeration of factions in the game."""

    ALLIANCE = 0
    HORDE = 1
    OTHER = 2

    __race_to_faction__ = {
        Race.NEUTRAL: OTHER,
        Race.HUMAN: ALLIANCE,
        Race.ORC: HORDE,
        Race.DWARF: ALLIANCE,
        Race.NIGHT_ELF: ALLIANCE,
        Race.UNDEAD: HORDE,
        Race.TAUREN: HORDE,
        Race.GNOME: ALLIANCE,
        Race.TROLL: HORDE,
        Race.GOBLIN: OTHER,
        Race.BLOOD_ELF: HORDE,
        Race.DRAENEI: ALLIANCE,
        Race.FEL_ORC: OTHER,
        Race.NAGA: OTHER,
        Race.BROKEN: OTHER,
        Race.SKELETON: OTHER,
        Race.VRYKUL: OTHER,
        Race.TUSKARR: OTHER,
        Race.FOREST_TROLL: OTHER,
        Race.TAUNKA: OTHER,
        Race.NORTREND_SKELETON: OTHER,
        Race.ICE_TROLL: OTHER,
    }

    @classmethod
    def from_race(cls, race: Race) -> "Faction":
        """Returns the faction based on the race."""
        return cls.__race_to_faction__.get(race, cls.OTHER)  # type: ignore[return-value]
