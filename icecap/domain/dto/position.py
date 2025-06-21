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
