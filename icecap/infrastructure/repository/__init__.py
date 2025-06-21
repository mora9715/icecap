"""This module provides repository classes for accessing different types of game entities.

The repositories abstract the data access layer and provide a clean interface
for retrieving and manipulating game entities.
"""

from .player_repository import PlayerRepository
from .unit_repository import UnitRepository
from .game_object_repository import GameObjectRepository

__all__ = ["PlayerRepository", "UnitRepository", "GameObjectRepository"]
