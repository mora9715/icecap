"""Data transfer objects for the application.

This module contains data structures used to transfer data between
different parts of the application.

"""

from .position import Position
from .unit_fields import UnitFields
from .game_object_fields import GameObjectFields

__all__ = ["Position", "UnitFields", "GameObjectFields"]
