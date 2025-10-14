"""Tests for game object repository."""

import struct
from unittest.mock import Mock
from icecap.infrastructure.repository.game_object_repository import GameObjectRepository
from icecap.domain.models import Entity, GameObject
from icecap.domain.enums import EntityType
from tests.utils import MemoryBuilder


class TestGameObjectRepositoryInitialization:
    """Test game object repository initialization."""

    def test_create_repository(self):
        """Test creating a game object repository."""
        mock_driver = Mock()
        repository = GameObjectRepository(mock_driver)

        assert repository.driver is mock_driver


class TestGameObjectRepositoryGetGameObjectFromEntity:
    """Test converting entity to game object."""

    def test_get_game_object_from_entity(self):
        """Test getting game object from entity with all fields."""
        # Setup
        entity = Entity(
            guid=0x0F00000000000001,
            object_address=0x20000000,
            entity_type=EntityType.GAME_OBJECT,
        )

        # Mock driver components
        mock_driver = Mock()

        # Mock object manager
        mock_object_manager = Mock()
        # Position data
        position_data = struct.pack("<fffff", 10.0, 20.0, 30.0, 0.0, 1.57)

        # Game object fields structure
        fields_address = 0x30000000
        memory = (
            MemoryBuilder()
            .with_bytes_at(0x20000000 + 0x190, position_data)  # Position
            .with_uint_at(0x20000000 + 0x8, fields_address)  # Fields pointer
            .with_ulonglong_at(fields_address, 0x0F00000000000001)  # guid
            .with_uint_at(fields_address + 8, 5)  # type
            .with_uint_at(fields_address + 12, 12345)  # entry
            .with_uint_at(fields_address + 32, 999)  # display_id
            .with_ulonglong_at(fields_address + 24, 0x0F00000000000002)  # created_by
            .with_uint_at(fields_address + 100, 1)  # state
            .build()
        )

        mock_object_manager.memory_manager = memory
        mock_object_manager.get_entity_position.return_value = Mock(
            x=20.0, y=10.0, z=30.0, rotation=1.57
        )
        mock_object_manager.get_game_object_fields.return_value = Mock(
            entry=12345, display_id=999, created_by=0x0F00000000000002, bytes1_state=1
        )

        # Mock name resolver
        mock_name_resolver = Mock()
        mock_name_resolver.resolve_game_object_name_by_entry_id.return_value = "Treasure Chest"

        repository = GameObjectRepository(mock_driver)

        # Execute
        game_object = repository.get_game_object_from_entity(
            entity, object_manager=mock_object_manager, name_resolver=mock_name_resolver
        )

        # Assert
        assert isinstance(game_object, GameObject)
        assert game_object.guid == entity.guid
        assert game_object.object_address == entity.object_address
        assert game_object.entity_type == EntityType.GAME_OBJECT
        assert game_object.name == "Treasure Chest"
        assert game_object.position.x == 20.0
        assert game_object.position.y == 10.0
        assert game_object.position.z == 30.0
        assert game_object.game_object_fields.entry_id == 12345
        assert game_object.game_object_fields.display_id == 999

    def test_get_game_object_uses_driver_defaults(self):
        """Test that get_game_object uses driver's object_manager and name_resolver by default."""
        entity = Entity(
            guid=0x0F00000000000001,
            object_address=0x20000000,
            entity_type=EntityType.GAME_OBJECT,
        )

        # Setup driver with default mocks
        mock_driver = Mock()
        mock_driver.object_manager.get_entity_position.return_value = Mock(
            x=1.0, y=2.0, z=3.0, rotation=0.0
        )
        mock_driver.object_manager.get_game_object_fields.return_value = Mock(
            entry=100, display_id=200, created_by=0, bytes1_state=0
        )
        mock_driver.name_resolver.resolve_game_object_name_by_entry_id.return_value = "Object"

        repository = GameObjectRepository(mock_driver)

        # Execute without providing object_manager or name_resolver
        game_object = repository.get_game_object_from_entity(entity)

        # Should have used driver's defaults
        assert game_object.name == "Object"
        mock_driver.object_manager.get_entity_position.assert_called_once()
        mock_driver.name_resolver.resolve_game_object_name_by_entry_id.assert_called_once()


class TestGameObjectRepositoryYieldGameObjects:
    """Test yielding game objects."""

    def test_yield_game_objects(self):
        """Test yielding all game objects from object manager."""
        # Create test entities
        entities = [
            Entity(guid=1, object_address=0x1000, entity_type=EntityType.GAME_OBJECT),
            Entity(guid=2, object_address=0x2000, entity_type=EntityType.UNIT),  # Not a game object
            Entity(guid=3, object_address=0x3000, entity_type=EntityType.GAME_OBJECT),
        ]

        # Mock driver
        mock_driver = Mock()
        mock_driver.object_manager.yield_objects.return_value = iter(entities)
        mock_driver.object_manager.get_entity_position.return_value = Mock(
            x=0.0, y=0.0, z=0.0, rotation=0.0
        )
        mock_driver.object_manager.get_game_object_fields.return_value = Mock(
            entry=1, display_id=1, created_by=0, bytes1_state=0
        )
        mock_driver.name_resolver.resolve_game_object_name_by_entry_id.return_value = "Object"

        repository = GameObjectRepository(mock_driver)

        # Execute
        game_objects = list(repository.yield_game_objects())

        # Should only yield the 2 game objects (entities with GAME_OBJECT type)
        assert len(game_objects) == 2
        assert all(isinstance(obj, GameObject) for obj in game_objects)
        assert game_objects[0].guid == 1
        assert game_objects[1].guid == 3

    def test_yield_game_objects_empty(self):
        """Test yielding game objects when none exist."""
        mock_driver = Mock()
        mock_driver.object_manager.yield_objects.return_value = iter([])

        repository = GameObjectRepository(mock_driver)

        game_objects = list(repository.yield_game_objects())

        assert len(game_objects) == 0

    def test_yield_game_objects_filters_non_game_objects(self):
        """Test that yield_game_objects filters out non-game objects."""
        entities = [
            Entity(guid=1, object_address=0x1000, entity_type=EntityType.UNIT),
            Entity(guid=2, object_address=0x2000, entity_type=EntityType.PLAYER),
            Entity(guid=3, object_address=0x3000, entity_type=EntityType.ITEM),
        ]

        mock_driver = Mock()
        mock_driver.object_manager.yield_objects.return_value = iter(entities)

        repository = GameObjectRepository(mock_driver)

        game_objects = list(repository.yield_game_objects())

        # Should yield no game objects
        assert len(game_objects) == 0


class TestGameObjectRepositoryRefreshGameObject:
    """Test refreshing game object data."""

    def test_refresh_game_object(self):
        """Test refreshing a game object with new data from memory."""
        # Original game object
        original = GameObject(
            guid=0x0F00000000000001,
            object_address=0x20000000,
            name="Treasure Chest",
            entity_type=EntityType.GAME_OBJECT,
            position=Mock(x=10.0, y=20.0, z=30.0, rotation=0.0),
            game_object_fields=Mock(entry_id=12345, display_id=999, owner_guid=0, state=0),
        )

        # Mock driver with updated data
        mock_driver = Mock()
        mock_driver.object_manager.get_entity_position.return_value = Mock(
            x=15.0,
            y=25.0,
            z=35.0,
            rotation=1.57,  # Updated position
        )
        mock_driver.object_manager.get_game_object_fields.return_value = Mock(
            entry=12345,
            display_id=999,
            created_by=0x0F00000000000002,
            bytes1_state=1,  # Updated state
        )

        repository = GameObjectRepository(mock_driver)

        # Execute
        refreshed = repository.refresh_game_object(original)

        # Verify refreshed data
        assert refreshed.guid == original.guid
        assert refreshed.object_address == original.object_address
        assert refreshed.name == original.name  # Name should be preserved
        assert refreshed.entity_type == EntityType.GAME_OBJECT

        # Position should be updated
        assert refreshed.position.x == 15.0
        assert refreshed.position.y == 25.0
        assert refreshed.position.z == 35.0

        # Fields should be updated
        assert refreshed.game_object_fields.state == 1

    def test_refresh_game_object_preserves_name(self):
        """Test that refresh preserves the original name."""
        original = GameObject(
            guid=1,
            object_address=0x1000,
            name="Original Name",
            entity_type=EntityType.GAME_OBJECT,
            position=Mock(x=0.0, y=0.0, z=0.0, rotation=0.0),
            game_object_fields=Mock(entry_id=1, display_id=1, owner_guid=0, state=0),
        )

        mock_driver = Mock()
        mock_driver.object_manager.get_entity_position.return_value = Mock(
            x=0.0, y=0.0, z=0.0, rotation=0.0
        )
        mock_driver.object_manager.get_game_object_fields.return_value = Mock(
            entry=1, display_id=1, created_by=0, bytes1_state=0
        )

        repository = GameObjectRepository(mock_driver)

        refreshed = repository.refresh_game_object(original)

        # Name should be preserved from original
        assert refreshed.name == "Original Name"
