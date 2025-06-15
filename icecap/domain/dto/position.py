from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    x: float
    y: float
    z: float
    yaw: float  # In radians
