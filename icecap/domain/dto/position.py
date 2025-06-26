from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Position:
    """Data class representing a 3D position with rotation."""

    x: float
    """The x-coordinate of the position."""

    y: float
    """The y-coordinate of the position."""

    z: float
    """The z-coordinate of the position."""

    rotation: float
    """The rotation angle in radians (0-2pi)."""

    def get_distance_to(self, other: "Position") -> float:
        """Calculates the distance to another position."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2) ** 0.5
