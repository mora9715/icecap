"""The name resolver interface."""

from typing import Protocol
from icecap.domain.models import Entity


class NameResolver(Protocol):
    """Resolves names for game entities within the game.

    This class provides methods to resolve names for different types of game entities
    such as units, players, and game objects.

    """

    def resolve_game_object_name_by_entry_id(self, entry_id: int) -> str:
        """Resolve the name of a game object by its entry ID."""

    def resolve_game_object_name_by_display_id(self, display_id: int) -> str:
        """Resolve the name of a game object by its display ID.

        Note that there is no uniqueness guarantee, as multiple game objects can share
        the same display ID. The method returns the first matching name found.
        """

    def resolve_name(self, entity: Entity) -> str:
        """Resolve the name of an entity based on its type.

        For game objects, use resolve_game_object_name_by_entry_id instead.
        """
