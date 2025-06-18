from icecap.infrastructure.memory_manager import MemoryManager

from .object_manager import ObjectManager
from .name_resolver import NameResolver

from .offsets import (
    CLIENT_CONNECTION_OFFSET,
    OBJECT_MANAGER_OFFSET,
    LOCAL_PLAYER_GUID_STATIC_OFFSET,
)


class GameDriver:
    """The driver is responsible for direct interaction with the game."""

    name_resolver: NameResolver

    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager

        self.name_resolver = NameResolver(memory_manager)

    def get_object_manager(self) -> ObjectManager:
        """Retrieves the Object Manager from the game client."""
        client_connection_address = self.get_client_connection_address()
        object_manager_address = self.get_object_manager_address(
            client_connection_address
        )
        return ObjectManager(self.memory_manager, object_manager_address)

    def get_client_connection_address(self) -> int:
        address = self.memory_manager.read_uint(CLIENT_CONNECTION_OFFSET)
        return address

    def get_object_manager_address(self, client_connection_address: int) -> int:
        address = self.memory_manager.read_uint(
            client_connection_address + OBJECT_MANAGER_OFFSET
        )
        return address

    def get_local_player_guid(self) -> int:
        """Retrieves the GUID of the local player.
        Uses static offset. This is less reliable than dynamic address,
        but it is faster and does not require reading the object manager.

        This is useful for quick checks or when the object manager is not available.
        For example, this can be used to check if the player is in the game world.
        """
        return self.memory_manager.read_ulonglong(LOCAL_PLAYER_GUID_STATIC_OFFSET)

    def is_player_in_game(self) -> bool:
        """Checks if the player is in the game world.

        Local player GUID is non-zero only when the player is in the game.
        """
        return self.get_local_player_guid() != 0
