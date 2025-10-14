"""Integration tests for repositories.

These tests verify that repositories work correctly with all their dependencies
(driver, object_manager, name_resolver) in realistic scenarios.
"""

import struct
from unittest.mock import Mock

from icecap.infrastructure.repository.game_object_repository import GameObjectRepository
from icecap.infrastructure.repository.unit_repository import UnitRepository
from icecap.domain.models import Entity, GameObject, Unit
from icecap.domain.enums import EntityType, Race, PlayerClass, Gender, Faction
from icecap.domain.dto import Position
from tests.utils import MemoryBuilder


class TestGameObjectRepositoryIntegration:
    """Test GameObjectRepository with all dependencies."""

    def test_full_game_object_pipeline(self):
        """Test complete pipeline: entity -> memory reads -> game object."""
        # Create entity
        entity = Entity(
            guid=0x0F00000000000001,
            object_address=0x20000000,
            entity_type=EntityType.GAME_OBJECT,
        )

        # Setup realistic memory layout
        fields_address = 0x30000000
        position_data = struct.pack("<fffff", 10.0, 20.0, 30.0, 0.0, 1.57)

        memory = (
            MemoryBuilder()
            # Position
            .with_bytes_at(0x20000000 + 0x190, position_data)
            # Fields pointer
            .with_uint_at(0x20000000 + 0x8, fields_address)
            # GameObject fields
            .with_ulonglong_at(fields_address, 0x0F00000000000001)  # guid
            .with_uint_at(fields_address + 8, 5)  # type
            .with_uint_at(fields_address + 12, 12345)  # entry
            .with_uint_at(fields_address + 16, 100)  # scale_x
            .with_uint_at(fields_address + 20, 0)  # padding
            .with_ulonglong_at(fields_address + 24, 0x0F00000000000002)  # created_by
            .with_uint_at(fields_address + 32, 999)  # display_id
            .with_uint_at(fields_address + 100, 1)  # state
            .build()
        )

        # Setup mocks
        mock_driver = Mock()
        mock_object_manager = Mock()
        mock_object_manager.memory_manager = memory

        # Mock position reading
        mock_object_manager.get_entity_position.return_value = Position(
            x=20.0, y=10.0, z=30.0, rotation=1.57
        )

        # Mock fields reading
        mock_object_manager.get_game_object_fields.return_value = Mock(
            entry=12345,
            display_id=999,
            created_by=0x0F00000000000002,
            bytes1_state=1,
        )

        # Mock name resolution
        mock_name_resolver = Mock()
        mock_name_resolver.resolve_game_object_name_by_entry_id.return_value = "Treasure Chest"

        # Create repository and test
        repository = GameObjectRepository(mock_driver)
        game_object = repository.get_game_object_from_entity(
            entity, object_manager=mock_object_manager, name_resolver=mock_name_resolver
        )

        # Verify complete transformation
        assert isinstance(game_object, GameObject)
        assert game_object.guid == entity.guid
        assert game_object.name == "Treasure Chest"
        assert game_object.position.x == 20.0
        assert game_object.position.y == 10.0
        assert game_object.position.z == 30.0
        assert game_object.game_object_fields.entry_id == 12345
        assert game_object.game_object_fields.display_id == 999

        # Verify all dependencies were called
        mock_object_manager.get_entity_position.assert_called_once()
        mock_object_manager.get_game_object_fields.assert_called_once()
        mock_name_resolver.resolve_game_object_name_by_entry_id.assert_called_once_with(12345)

    def test_yield_game_objects_filters_correctly(self):
        """Test that yielding game objects filters and transforms correctly."""
        # Create mixed entities
        entities = [
            Entity(guid=1, object_address=0x1000, entity_type=EntityType.GAME_OBJECT),
            Entity(guid=2, object_address=0x2000, entity_type=EntityType.UNIT),
            Entity(guid=3, object_address=0x3000, entity_type=EntityType.GAME_OBJECT),
            Entity(guid=4, object_address=0x4000, entity_type=EntityType.PLAYER),
            Entity(guid=5, object_address=0x5000, entity_type=EntityType.GAME_OBJECT),
        ]

        # Setup driver mock
        mock_driver = Mock()
        mock_driver.object_manager.yield_objects.return_value = iter(entities)
        mock_driver.object_manager.get_entity_position.return_value = Position(0, 0, 0, 0)
        mock_driver.object_manager.get_game_object_fields.return_value = Mock(
            entry=1, display_id=1, created_by=0, bytes1_state=0
        )
        mock_driver.name_resolver.resolve_game_object_name_by_entry_id.return_value = "Object"

        # Test yielding
        repository = GameObjectRepository(mock_driver)
        game_objects = list(repository.yield_game_objects())

        # Should only get the 3 game objects
        assert len(game_objects) == 3
        assert all(isinstance(obj, GameObject) for obj in game_objects)
        assert game_objects[0].guid == 1
        assert game_objects[1].guid == 3
        assert game_objects[2].guid == 5


class TestUnitRepositoryIntegration:
    """Test UnitRepository with all dependencies."""

    def test_full_unit_pipeline(self):
        """Test complete pipeline: entity -> memory reads -> unit."""
        entity = Entity(
            guid=0x0F00000000000001,
            object_address=0x20000000,
            entity_type=EntityType.UNIT,
        )

        # Setup realistic memory
        fields_address = 0x30000000
        position_data = struct.pack("<fffff", 100.0, 200.0, 50.0, 0.0, 3.14)

        memory = (
            MemoryBuilder()
            .with_bytes_at(0x20000000 + 0xE8, position_data)  # Unit position offset
            .with_uint_at(0x20000000 + 0x8, fields_address)
            # Unit fields (simplified)
            .with_ulonglong_at(fields_address, 0x0F00000000000001)
            .with_uint_at(fields_address + 100, 5000)  # health
            .with_uint_at(fields_address + 104, 6000)  # max_health
            .with_uint_at(fields_address + 200, 60)  # level
            .build()
        )

        # Setup mocks
        mock_driver = Mock()
        mock_object_manager = Mock()
        mock_object_manager.memory_manager = memory
        mock_object_manager.get_entity_position.return_value = Position(
            x=200.0, y=100.0, z=50.0, rotation=3.14
        )
        mock_object_manager.get_unit_fields.return_value = Mock(
            bytes_0_race=Race.HUMAN.value,
            bytes_0_class=PlayerClass.WARRIOR.value,
            bytes_0_gender=Gender.MALE.value,
            level=60,
            health=5000,
            max_health=6000,
        )

        mock_name_resolver = Mock()
        mock_name_resolver.resolve_name.return_value = "Elite Guard"

        # Create repository and test
        repository = UnitRepository(mock_driver)
        unit = repository.get_unit_from_entity(
            entity, object_manager=mock_object_manager, name_resolver=mock_name_resolver
        )

        # Verify complete transformation
        assert isinstance(unit, Unit)
        assert unit.guid == entity.guid
        assert unit.name == "Elite Guard"
        assert unit.position.x == 200.0
        assert unit.position.y == 100.0
        assert unit.unit_fields.level == 60
        assert unit.unit_fields.hit_points == 5000
        assert unit.unit_fields.max_hit_points == 6000
        assert unit.unit_fields.race == Race.HUMAN
        assert unit.unit_fields.player_class == PlayerClass.WARRIOR
        assert unit.unit_fields.faction == Faction.ALLIANCE.value  # Derived from race

        # Verify dependencies called
        mock_object_manager.get_entity_position.assert_called_once()
        mock_object_manager.get_unit_fields.assert_called_once()
        mock_name_resolver.resolve_name.assert_called_once()

    def test_faction_derivation_for_all_races(self):
        """Test that faction is correctly derived for all playable races."""
        test_cases = [
            (Race.HUMAN, Faction.ALLIANCE),
            (Race.ORC, Faction.HORDE),
            (Race.DWARF, Faction.ALLIANCE),
            (Race.NIGHT_ELF, Faction.ALLIANCE),
            (Race.UNDEAD, Faction.HORDE),
            (Race.TAUREN, Faction.HORDE),
            (Race.GNOME, Faction.ALLIANCE),
            (Race.TROLL, Faction.HORDE),
        ]

        for race, expected_faction in test_cases:
            entity = Entity(guid=1, object_address=0x1000, entity_type=EntityType.UNIT)

            mock_driver = Mock()
            mock_driver.object_manager.get_entity_position.return_value = Position(0, 0, 0, 0)
            mock_driver.object_manager.get_unit_fields.return_value = Mock(
                bytes_0_race=race.value,
                bytes_0_class=PlayerClass.WARRIOR.value,
                bytes_0_gender=Gender.MALE.value,
                level=1,
                health=100,
                max_health=100,
            )
            mock_driver.name_resolver.resolve_name.return_value = "Unit"

            repository = UnitRepository(mock_driver)
            unit = repository.get_unit_from_entity(entity)

            assert unit.unit_fields.faction == expected_faction.value, (
                f"Failed for {race.name}: expected {expected_faction.name}"
            )


class TestRepositoryRefreshIntegration:
    """Test repository refresh methods with state changes."""

    def test_game_object_refresh_updates_state(self):
        """Test that refreshing a game object picks up state changes."""
        # Initial game object
        original = GameObject(
            guid=0x0F00000000000001,
            object_address=0x20000000,
            name="Door",
            entity_type=EntityType.GAME_OBJECT,
            position=Position(x=10.0, y=20.0, z=30.0, rotation=0.0),
            game_object_fields=Mock(entry_id=1234, display_id=100, owner_guid=0, state=0),
        )

        # Setup mock driver with updated state
        mock_driver = Mock()
        mock_driver.object_manager.get_entity_position.return_value = Position(
            x=10.0,
            y=20.0,
            z=30.0,
            rotation=1.57,  # Door rotated
        )
        mock_driver.object_manager.get_game_object_fields.return_value = Mock(
            entry=1234,
            display_id=100,
            created_by=0,
            bytes1_state=1,  # Door opened!
        )

        # Refresh
        repository = GameObjectRepository(mock_driver)
        refreshed = repository.refresh_game_object(original)

        # Verify state changed
        assert refreshed.name == "Door"  # Name preserved
        assert refreshed.position.rotation == 1.57  # Position updated
        assert refreshed.game_object_fields.state == 1  # State updated

    def test_unit_refresh_updates_health(self):
        """Test that refreshing a unit picks up health changes."""
        original = Unit(
            guid=0x0F00000000000001,
            object_address=0x20000000,
            name="Guard",
            entity_type=EntityType.UNIT,
            position=Position(x=0, y=0, z=0, rotation=0),
            unit_fields=Mock(
                level=50,
                hit_points=5000,
                max_hit_points=5000,
                faction=Faction.ALLIANCE,
                race=Race.HUMAN,
                player_class=PlayerClass.WARRIOR,
                gender=Gender.MALE,
            ),
        )

        # Setup mock with damaged unit
        mock_driver = Mock()
        mock_driver.object_manager.get_entity_position.return_value = Position(5, 5, 0, 0)
        mock_driver.object_manager.get_unit_fields.return_value = Mock(
            level=50,
            health=1000,  # Took damage!
            max_health=5000,
        )

        # Refresh
        repository = UnitRepository(mock_driver)
        refreshed = repository.refresh_unit(original)

        # Verify health updated but other fields preserved
        assert refreshed.name == "Guard"
        assert refreshed.unit_fields.hit_points == 1000
        assert refreshed.unit_fields.max_hit_points == 5000
        assert refreshed.unit_fields.race == Race.HUMAN
        assert refreshed.position.x == 5  # Moved
