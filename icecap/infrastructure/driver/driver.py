"""The game driver."""

from icecap.infrastructure.memory_manager import MemoryManager

from .object_manager import ObjectManager
from .name_resolver import NameResolver

from .offsets import (
    CLIENT_CONNECTION_OFFSET,
    OBJECT_MANAGER_OFFSET,
    LOCAL_PLAYER_GUID_STATIC_OFFSET,
)


class GameDriver:
    """Provides an interface to interact with the game's memory and objects.

    It serves as the main entry point for low-level accessing game data and functionality.

    """

    name_resolver: NameResolver
    """Name resolver for resolving names of game objects and entities."""

    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager

        self.name_resolver = NameResolver(memory_manager)

    def get_object_manager(self) -> ObjectManager:
        """Retrieve the Object Manager from the game client."""
        client_connection_address = self.get_client_connection_address()
        object_manager_address = self.get_object_manager_address(client_connection_address)
        return ObjectManager(self.memory_manager, object_manager_address)

    def get_client_connection_address(self) -> int:
        """This method reads the client connection address from memory using a static offset."""
        address = self.memory_manager.read_uint(CLIENT_CONNECTION_OFFSET)
        return address

    def get_object_manager_address(self, client_connection_address: int) -> int:
        """Get the address of the object manager.

        This method reads the object manager address from memory using the client
        connection address and a static offset.
        """
        address = self.memory_manager.read_uint(client_connection_address + OBJECT_MANAGER_OFFSET)
        return address

    def get_local_player_guid(self) -> int:
        """Retrieve the GUID of the local player using a static offset.

        Uses static offset which is less reliable than dynamic address,
        but it is faster and does not require reading the object manager.

        This is useful for quick checks or when the object manager is not available.
        For example, this can be used to check if the player is in the game world.
        """
        return self.memory_manager.read_ulonglong(LOCAL_PLAYER_GUID_STATIC_OFFSET)

    def is_player_in_game(self) -> bool:
        """Check if the player is in the game world.

        This method uses the local player GUID to determine if the player is in the game.
        The GUID is non-zero only when the player is in the game.
        """
        return self.get_local_player_guid() != 0
