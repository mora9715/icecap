"""
This module initializes the domain models for the Icecap project.
"""

from .entity import Entity
from .player import Player
from .unit import Unit
from .game_objects import GameObject

__all__ = ["Entity", "Player", "Unit", "GameObject"]
