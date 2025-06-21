"""
This module contains models that represent various game entities.
All models are **read-only** and represent the state of the game at a specific point in time.

**Important note:** The models do not contain all fields of the game entities.
For ah exhaustive list of available data,
please refer to the **C structs** definitions in the infrastructure layer.
"""

from .entity import Entity
from .player import Player
from .unit import Unit
from .game_objects import GameObject

__all__ = ["Entity", "Player", "Unit", "GameObject"]
