"""Global pytest configuration and fixtures for IceCap tests."""

import pytest
from unittest.mock import Mock, MagicMock

from icecap.domain.models import Entity
from icecap.domain.enums import EntityType
from icecap.domain.dto import Position


@pytest.fixture
def sample_entity():
    """Provides a basic Entity object for testing."""
    return Entity(guid=12345, object_address=0x1000, entity_type=EntityType.PLAYER)


@pytest.fixture
def sample_position():
    """Provides a basic Position DTO for testing."""
    return Position(x=100.0, y=200.0, z=300.0, rotation=1.5)


@pytest.fixture
def mock_memory_manager():
    """Provides a mocked MemoryManager for testing."""
    mock = Mock()
    mock.read_uint = Mock(return_value=0x12345)
    mock.read_ulonglong = Mock(return_value=123456789)
    mock.read_float = Mock(return_value=1.5)
    mock.read_bytes = Mock(return_value=b"\x00\x01\x02\x03")
    return mock


@pytest.fixture
def mock_process_manager():
    """Provides a mocked GameProcessManager for testing."""
    mock = Mock()
    mock.get_process_id = Mock(return_value=1234)
    mock.pid_changed_since_last_call = Mock(return_value=False)
    return mock


@pytest.fixture
def mock_object_manager():
    """Provides a mocked ObjectManager for testing."""
    mock = Mock()
    mock.address = 0x5000
    mock.yield_objects = Mock(return_value=iter([]))
    mock.get_entity_position = Mock(return_value=Position(100.0, 200.0, 300.0, 1.5))
    return mock


@pytest.fixture
def mock_name_resolver():
    """Provides a mocked NameResolver for testing."""
    mock = Mock()
    mock.resolve_game_object_name_by_entry_id = Mock(return_value="Test Object")
    mock.resolve_unit_name = Mock(return_value="Test Unit")
    return mock


@pytest.fixture
def mock_driver(mock_process_manager, mock_memory_manager, mock_object_manager, mock_name_resolver):
    """Provides a fully mocked GameDriver for testing."""
    mock = MagicMock()
    mock.game_process_manager = mock_process_manager
    mock.memory_manager = mock_memory_manager
    mock.object_manager = mock_object_manager
    mock.name_resolver = mock_name_resolver
    mock.get_local_player_guid = Mock(return_value=999)
    mock.is_player_in_game = Mock(return_value=True)
    mock.is_game_running = Mock(return_value=True)
    return mock
