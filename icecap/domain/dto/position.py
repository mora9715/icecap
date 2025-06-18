from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    x: float
    y: float
    z: float
    rotation: float  # In radians
