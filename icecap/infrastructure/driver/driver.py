"""The game driver."""

from icecap.infrastructure.memory_manager import MemoryManager, MemoryManagerGetter
from icecap.infrastructure.process import GameProcessManager
from .object_manager import ObjectManager
from icecap.infrastructure.name_resolver import NameResolver, get_name_resolver

from .offsets import (
    CLIENT_CONNECTION_OFFSET,
    OBJECT_MANAGER_OFFSET,
    LOCAL_PLAYER_GUID_STATIC_OFFSET,
)


class GameDriver:
    """Provides an interface to interact with the game's memory and objects.

    It serves as the main entry point for low-level accessing game data and functionality.

    """

    game_process_manager: GameProcessManager
    """Game process manager for interacting with the game process."""

    memory_manager_getter: MemoryManagerGetter
    """Callable that returns a MemoryManager instance for the game process.

    This is used to access the game's memory and objects. Can't use static memory_manager
    because game process may change.
    """

    def __init__(
        self, game_process_manager: GameProcessManager, memory_manager_getter: MemoryManagerGetter
    ):
        self.game_process_manager = game_process_manager
        self.memory_manager_getter = memory_manager_getter

        self._name_resolver: NameResolver | None = None
        self._memory_manager: MemoryManager | None = None
        self._object_manager: ObjectManager | None = None
        self._last_known_object_manager_address: int | None = None

    @property
    def name_resolver(self) -> NameResolver:
        """A name resolver instance for resolving names of game entities.

        The attribute may return different objects depending on the state of the driver.
        """
        if not self._name_resolver:
            self._name_resolver = get_name_resolver(self.memory_manager)
            return self._name_resolver

        return self._name_resolver

    @property
    def memory_manager(self) -> MemoryManager:
        """A memory manager instance for accessing the game's memory.

        The attribute may return different objects depending on the state of the driver.
        """
        if not self._memory_manager:
            self._memory_manager = self._get_memory_manager()
            return self._memory_manager

        if self.game_process_manager.pid_changed_since_last_call():
            self._memory_manager = self._get_memory_manager()

            # Existing name resolver and object manager
            # must be invalidated as they depend on the memory manager
            self._name_resolver = None
            self._object_manager = None

        return self._memory_manager

    @property
    def object_manager(self) -> ObjectManager:
        """The object manager instance for accessing the game's objects.

        The attribute may return different objects depending on the state of the driver.
        """
        if not self._object_manager:
            self._object_manager = self._get_object_manager()
            self._last_known_object_manager_address = self._object_manager.address
            return self._object_manager

        if self._last_known_object_manager_address != self._get_object_manager_address(
            self.get_client_connection_address()
        ):
            self._object_manager = self._get_object_manager()
            self._last_known_object_manager_address = self._object_manager.address

        return self._object_manager

    def _get_memory_manager(self) -> MemoryManager:
        process_id = self.game_process_manager.get_process_id()

        if not process_id:
            raise RuntimeError("Game process is not running.")
        return self.memory_manager_getter(process_id)

    def _get_object_manager(self) -> ObjectManager:
        client_connection_address = self.get_client_connection_address()
        object_manager_address = self._get_object_manager_address(client_connection_address)
        return ObjectManager(self.memory_manager, object_manager_address)

    def get_client_connection_address(self) -> int:
        """This method reads the client connection address from memory using a static offset."""
        address = self.memory_manager.read_uint(CLIENT_CONNECTION_OFFSET)
        return address

    def _get_object_manager_address(self, client_connection_address: int) -> int:
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

    def is_game_running(self) -> bool:
        """Check if the game is running."""

        return bool(self.game_process_manager.get_process_id())
