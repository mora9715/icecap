import pytest
from unittest.mock import Mock
from icecap.infrastructure.driver.driver import GameDriver
from tests.utils import MockMemoryManager, MemoryBuilder
from icecap.infrastructure.driver.offsets import (
    CLIENT_CONNECTION_OFFSET,
    OBJECT_MANAGER_OFFSET,
    LOCAL_PLAYER_GUID_STATIC_OFFSET,
)


class TestGameDriverProperties:
    """Test GameDriver property management and caching."""

    def test_memory_manager_property_caching(self):
        mock_process_manager = Mock()
        mock_process_manager.get_process_id.return_value = 1234
        mock_process_manager.pid_changed_since_last_call.return_value = False

        mock_memory_getter = Mock(return_value=MockMemoryManager())

        driver = GameDriver(mock_process_manager, mock_memory_getter)

        mem1 = driver.memory_manager
        mem2 = driver.memory_manager

        # Should return the same instance
        assert mem1 is mem2
        # Memory getter should be called only once
        assert mock_memory_getter.call_count == 1

    def test_memory_manager_invalidation_on_pid_change(self):
        """Test that memory_manager is invalidated when PID changes."""
        mock_process_manager = Mock()
        mock_process_manager.get_process_id.return_value = 1234

        # First call: no change, second call: PID changed
        mock_process_manager.pid_changed_since_last_call.side_effect = [
            False,
            True,
            False,
        ]

        mock_memory_getter = Mock(side_effect=[MockMemoryManager(), MockMemoryManager()])

        driver = GameDriver(mock_process_manager, mock_memory_getter)

        mem1 = driver.memory_manager
        mem2 = driver.memory_manager  # Should return cached
        mem3 = driver.memory_manager  # PID changed, should create new

        assert mem1 is mem2
        assert mem1 is not mem3
        # Memory getter should be called twice (initial + after PID change)
        assert mock_memory_getter.call_count == 2

    def test_name_resolver_property_caching(self):
        """Test that name_resolver is cached."""
        mock_process_manager = Mock()
        mock_process_manager.get_process_id.return_value = 1234
        mock_process_manager.pid_changed_since_last_call.return_value = False

        mock_memory_getter = Mock(return_value=MockMemoryManager())

        driver = GameDriver(mock_process_manager, mock_memory_getter)

        resolver1 = driver.name_resolver
        resolver2 = driver.name_resolver

        # Should return the same instance
        assert resolver1 is resolver2

    def test_object_manager_property_caching(self):
        """Test that object_manager is cached."""
        mock_process_manager = Mock()
        mock_process_manager.get_process_id.return_value = 1234
        mock_process_manager.pid_changed_since_last_call.return_value = False

        # Create memory with client connection and object manager addresses
        memory = (
            MemoryBuilder()
            .with_uint_at(
                CLIENT_CONNECTION_OFFSET, 0x12345678
            )  # CLIENT_CONNECTION_OFFSET -> connection address
            .with_uint_at(0x12345678 + OBJECT_MANAGER_OFFSET, 0x87654321)  # Object manager address
            .build()
        )

        mock_memory_getter = Mock(return_value=memory)

        driver = GameDriver(mock_process_manager, mock_memory_getter)

        obj_mgr1 = driver.object_manager
        obj_mgr2 = driver.object_manager

        # Should return the same instance
        assert obj_mgr1 is obj_mgr2

    def test_object_manager_invalidation_on_address_change(self):
        """Test that object_manager is invalidated when address changes."""
        mock_process_manager = Mock()
        mock_process_manager.get_process_id.return_value = 1234
        mock_process_manager.pid_changed_since_last_call.return_value = False

        # Create two different memory states with different object manager addresses
        memory1 = (
            MemoryBuilder()
            .with_uint_at(CLIENT_CONNECTION_OFFSET, 0x12345678)
            .with_uint_at(
                0x12345678 + OBJECT_MANAGER_OFFSET, 0x87654321
            )  # First object manager address
            .build()
        )

        memory2 = (
            MemoryBuilder()
            .with_uint_at(CLIENT_CONNECTION_OFFSET, 0x12345678)
            .with_uint_at(
                0x12345678 + OBJECT_MANAGER_OFFSET, 0x99999999
            )  # Different object manager address
            .build()
        )

        mock_memory_getter = Mock(side_effect=[memory1, memory2])

        # Create driver with first memory
        driver = GameDriver(mock_process_manager, mock_memory_getter)
        obj_mgr1 = driver.object_manager

        # Manually change memory to trigger address change
        driver._memory_manager = memory2

        obj_mgr2 = driver.object_manager

        # Should create new object manager due to address change
        assert obj_mgr1.address != obj_mgr2.address


class TestGameDriverMethods:
    """Test GameDriver methods."""

    def test_get_local_player_guid(self):
        """Test retrieving local player GUID."""
        from icecap.infrastructure.driver.offsets import LOCAL_PLAYER_GUID_STATIC_OFFSET

        mock_process_manager = Mock()
        mock_process_manager.get_process_id.return_value = 1234
        mock_process_manager.pid_changed_since_last_call.return_value = False

        # Create memory with local player GUID
        guid = 0x0F00000000001234
        memory = MemoryBuilder().with_ulonglong_at(LOCAL_PLAYER_GUID_STATIC_OFFSET, guid).build()

        mock_memory_getter = Mock(return_value=memory)

        driver = GameDriver(mock_process_manager, mock_memory_getter)

        result = driver.get_local_player_guid()

        assert result == guid

    def test_is_player_in_game_true(self):
        """Test checking if player is in game (GUID is non-zero)."""
        from icecap.infrastructure.driver.offsets import LOCAL_PLAYER_GUID_STATIC_OFFSET

        mock_process_manager = Mock()
        mock_process_manager.get_process_id.return_value = 1234
        mock_process_manager.pid_changed_since_last_call.return_value = False

        memory = (
            MemoryBuilder()
            .with_ulonglong_at(LOCAL_PLAYER_GUID_STATIC_OFFSET, 0x0F00000000001234)
            .build()
        )

        mock_memory_getter = Mock(return_value=memory)

        driver = GameDriver(mock_process_manager, mock_memory_getter)

        assert driver.is_player_in_game() is True

    def test_is_player_in_game_false(self):
        """Test checking if player is not in game (GUID is zero)."""
        from icecap.infrastructure.driver.offsets import LOCAL_PLAYER_GUID_STATIC_OFFSET

        mock_process_manager = Mock()
        mock_process_manager.get_process_id.return_value = 1234
        mock_process_manager.pid_changed_since_last_call.return_value = False

        memory = MemoryBuilder().with_ulonglong_at(LOCAL_PLAYER_GUID_STATIC_OFFSET, 0).build()

        mock_memory_getter = Mock(return_value=memory)

        driver = GameDriver(mock_process_manager, mock_memory_getter)

        assert driver.is_player_in_game() is False

    def test_is_game_running_true(self):
        """Test checking if game is running."""
        mock_process_manager = Mock()
        mock_process_manager.get_process_id.return_value = 1234

        mock_memory_getter = Mock(return_value=MockMemoryManager())

        driver = GameDriver(mock_process_manager, mock_memory_getter)

        assert driver.is_game_running() is True

    def test_is_game_running_false(self):
        """Test checking if game is not running."""
        mock_process_manager = Mock()
        mock_process_manager.get_process_id.return_value = None

        mock_memory_getter = Mock(return_value=MockMemoryManager())

        driver = GameDriver(mock_process_manager, mock_memory_getter)

        assert driver.is_game_running() is False

    def test_get_client_connection_address(self):
        """Test getting client connection address."""
        mock_process_manager = Mock()
        mock_process_manager.get_process_id.return_value = 1234
        mock_process_manager.pid_changed_since_last_call.return_value = False

        connection_address = 0x12345678
        memory = MemoryBuilder().with_uint_at(CLIENT_CONNECTION_OFFSET, connection_address).build()

        mock_memory_getter = Mock(return_value=memory)

        driver = GameDriver(mock_process_manager, mock_memory_getter)

        result = driver.get_client_connection_address()

        assert result == connection_address

    def test_memory_manager_raises_error_when_game_not_running(self):
        """Test that accessing memory_manager raises error when game is not running."""
        mock_process_manager = Mock()
        mock_process_manager.get_process_id.return_value = None

        mock_memory_getter = Mock()

        driver = GameDriver(mock_process_manager, mock_memory_getter)

        with pytest.raises(RuntimeError, match="Game process is not running"):
            _ = driver.memory_manager


class TestGameDriverIntegration:
    """Integration tests for GameDriver."""

    def test_full_initialization_flow(self):
        """Test complete driver initialization flow."""
        mock_process_manager = Mock()
        mock_process_manager.get_process_id.return_value = 1234
        mock_process_manager.pid_changed_since_last_call.return_value = False

        # Setup complete memory layout
        memory = (
            MemoryBuilder()
            .with_uint_at(CLIENT_CONNECTION_OFFSET, 0x12345678)  # Client connection
            .with_uint_at(0x12345678 + OBJECT_MANAGER_OFFSET, 0x87654321)  # Object manager
            .with_ulonglong_at(
                LOCAL_PLAYER_GUID_STATIC_OFFSET, 0x0F00000000001234
            )  # Local player GUID
            .build()
        )

        mock_memory_getter = Mock(return_value=memory)

        driver = GameDriver(mock_process_manager, mock_memory_getter)

        # All properties should be accessible
        assert driver.memory_manager is not None
        assert driver.name_resolver is not None
        assert driver.object_manager is not None
        assert driver.is_game_running() is True
        assert driver.is_player_in_game() is True
