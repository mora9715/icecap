"""Tests for unit repository."""

from unittest.mock import Mock
from icecap.infrastructure.repository.unit_repository import UnitRepository
from icecap.domain.models import Entity, Unit
from icecap.domain.enums import EntityType, Faction, Race, PlayerClass, Gender


class TestUnitRepositoryInitialization:
    """Test unit repository initialization."""

    def test_create_repository(self):
        """Test creating a unit repository."""
        mock_driver = Mock()
        repository = UnitRepository(mock_driver)

        assert repository.driver is mock_driver


class TestUnitRepositoryGetUnitFromEntity:
    """Test converting entity to unit."""

    def test_get_unit_from_entity(self):
        """Test getting unit from entity with all fields."""
        entity = Entity(
            guid=0x0F00000000000001,
            object_address=0x20000000,
            entity_type=EntityType.UNIT,
        )

        # Mock driver components
        mock_driver = Mock()
        mock_object_manager = Mock()
        mock_object_manager.get_entity_position.return_value = Mock(
            x=100.0, y=200.0, z=50.0, rotation=3.14
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

        repository = UnitRepository(mock_driver)

        # Execute
        unit = repository.get_unit_from_entity(
            entity, object_manager=mock_object_manager, name_resolver=mock_name_resolver
        )

        # Assert
        assert isinstance(unit, Unit)
        assert unit.guid == entity.guid
        assert unit.object_address == entity.object_address
        assert unit.entity_type == EntityType.UNIT
        assert unit.name == "Elite Guard"
        assert unit.position.x == 100.0
        assert unit.position.y == 200.0
        assert unit.position.z == 50.0
        assert unit.unit_fields.level == 60
        assert unit.unit_fields.hit_points == 5000
        assert unit.unit_fields.max_hit_points == 6000
        assert unit.unit_fields.race == Race.HUMAN
        assert unit.unit_fields.player_class == PlayerClass.WARRIOR
        assert unit.unit_fields.gender == Gender.MALE
        assert unit.unit_fields.faction == Faction.ALLIANCE.value  # From race

    def test_get_unit_uses_driver_defaults(self):
        """Test that get_unit uses driver's object_manager and name_resolver by default."""
        entity = Entity(
            guid=0x0F00000000000001,
            object_address=0x20000000,
            entity_type=EntityType.UNIT,
        )

        mock_driver = Mock()
        mock_driver.object_manager.get_entity_position.return_value = Mock(
            x=0.0, y=0.0, z=0.0, rotation=0.0
        )
        mock_driver.object_manager.get_unit_fields.return_value = Mock(
            bytes_0_race=Race.ORC.value,
            bytes_0_class=PlayerClass.WARRIOR.value,
            bytes_0_gender=Gender.MALE.value,
            level=1,
            health=100,
            max_health=100,
        )
        mock_driver.name_resolver.resolve_name.return_value = "Grunt"

        repository = UnitRepository(mock_driver)

        # Execute without providing object_manager or name_resolver
        unit = repository.get_unit_from_entity(entity)

        # Should have used driver's defaults
        assert unit.name == "Grunt"
        mock_driver.object_manager.get_entity_position.assert_called_once()
        mock_driver.name_resolver.resolve_name.assert_called_once()

    def test_get_unit_faction_from_race(self):
        """Test that faction is correctly derived from race."""
        test_cases = [
            (Race.HUMAN, Faction.ALLIANCE),
            (Race.ORC, Faction.HORDE),
            (Race.DWARF, Faction.ALLIANCE),
            (Race.TAUREN, Faction.HORDE),
            (Race.NIGHT_ELF, Faction.ALLIANCE),
            (Race.UNDEAD, Faction.HORDE),
        ]

        for race, expected_faction in test_cases:
            entity = Entity(guid=1, object_address=0x1000, entity_type=EntityType.UNIT)

            mock_driver = Mock()
            mock_driver.object_manager.get_entity_position.return_value = Mock(
                x=0.0, y=0.0, z=0.0, rotation=0.0
            )
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

            assert unit.unit_fields.faction == expected_faction.value


class TestUnitRepositoryYieldUnits:
    """Test yielding units."""

    def test_yield_units(self):
        """Test yielding all units from object manager."""
        entities = [
            Entity(guid=1, object_address=0x1000, entity_type=EntityType.UNIT),
            Entity(guid=2, object_address=0x2000, entity_type=EntityType.GAME_OBJECT),  # Not a unit
            Entity(guid=3, object_address=0x3000, entity_type=EntityType.UNIT),
        ]

        mock_driver = Mock()
        mock_driver.object_manager.yield_objects.return_value = iter(entities)
        mock_driver.object_manager.get_entity_position.return_value = Mock(
            x=0.0, y=0.0, z=0.0, rotation=0.0
        )
        mock_driver.object_manager.get_unit_fields.return_value = Mock(
            bytes_0_race=Race.HUMAN.value,
            bytes_0_class=PlayerClass.WARRIOR.value,
            bytes_0_gender=Gender.MALE.value,
            level=1,
            health=100,
            max_health=100,
        )
        mock_driver.name_resolver.resolve_name.return_value = "Unit"

        repository = UnitRepository(mock_driver)

        # Execute
        units = list(repository.yield_units())

        # Should only yield the 2 units
        assert len(units) == 2
        assert all(isinstance(unit, Unit) for unit in units)
        assert units[0].guid == 1
        assert units[1].guid == 3

    def test_yield_units_empty(self):
        """Test yielding units when none exist."""
        mock_driver = Mock()
        mock_driver.object_manager.yield_objects.return_value = iter([])

        repository = UnitRepository(mock_driver)

        units = list(repository.yield_units())

        assert len(units) == 0

    def test_yield_units_filters_non_units(self):
        """Test that yield_units filters out non-unit entities."""
        entities = [
            Entity(guid=1, object_address=0x1000, entity_type=EntityType.GAME_OBJECT),
            Entity(
                guid=2, object_address=0x2000, entity_type=EntityType.PLAYER
            ),  # PLAYER is not UNIT
            Entity(guid=3, object_address=0x3000, entity_type=EntityType.ITEM),
        ]

        mock_driver = Mock()
        mock_driver.object_manager.yield_objects.return_value = iter(entities)

        repository = UnitRepository(mock_driver)

        units = list(repository.yield_units())

        # Should yield no units
        assert len(units) == 0


class TestUnitRepositoryRefreshUnit:
    """Test refreshing unit data."""

    def test_refresh_unit(self):
        """Test refreshing a unit with new data from memory."""
        original = Unit(
            guid=0x0F00000000000001,
            object_address=0x20000000,
            name="Guard",
            entity_type=EntityType.UNIT,
            position=Mock(x=10.0, y=20.0, z=30.0, rotation=0.0),
            unit_fields=Mock(
                level=50,
                hit_points=1000,
                max_hit_points=2000,
                faction=Faction.ALLIANCE,
                race=Race.HUMAN,
                player_class=PlayerClass.WARRIOR,
                gender=Gender.MALE,
            ),
        )

        # Mock driver with updated data
        mock_driver = Mock()
        mock_driver.object_manager.get_entity_position.return_value = Mock(
            x=15.0,
            y=25.0,
            z=35.0,
            rotation=1.57,  # Updated position
        )
        mock_driver.object_manager.get_unit_fields.return_value = Mock(
            level=51,  # Level increased
            health=1500,  # Health changed
            max_health=2100,  # Max health increased
        )

        repository = UnitRepository(mock_driver)

        # Execute
        refreshed = repository.refresh_unit(original)

        # Verify refreshed data
        assert refreshed.guid == original.guid
        assert refreshed.object_address == original.object_address
        assert refreshed.name == original.name  # Name preserved
        assert refreshed.entity_type == EntityType.UNIT

        # Position updated
        assert refreshed.position.x == 15.0
        assert refreshed.position.y == 25.0

        # Stats updated
        assert refreshed.unit_fields.level == 51
        assert refreshed.unit_fields.hit_points == 1500
        assert refreshed.unit_fields.max_hit_points == 2100

        # Preserved fields
        assert refreshed.unit_fields.faction == Faction.ALLIANCE
        assert refreshed.unit_fields.race == Race.HUMAN
        assert refreshed.unit_fields.player_class == PlayerClass.WARRIOR
        assert refreshed.unit_fields.gender == Gender.MALE

    def test_refresh_unit_preserves_immutable_fields(self):
        """Test that refresh preserves immutable fields like name, race, class."""
        original = Unit(
            guid=1,
            object_address=0x1000,
            name="Original Name",
            entity_type=EntityType.UNIT,
            position=Mock(x=0.0, y=0.0, z=0.0, rotation=0.0),
            unit_fields=Mock(
                level=1,
                hit_points=100,
                max_hit_points=100,
                faction=Faction.ALLIANCE,
                race=Race.HUMAN,
                player_class=PlayerClass.WARRIOR,
                gender=Gender.MALE,
            ),
        )

        mock_driver = Mock()
        mock_driver.object_manager.get_entity_position.return_value = Mock(
            x=0.0, y=0.0, z=0.0, rotation=0.0
        )
        mock_driver.object_manager.get_unit_fields.return_value = Mock(
            level=2, health=200, max_health=200
        )

        repository = UnitRepository(mock_driver)

        refreshed = repository.refresh_unit(original)

        # Immutable fields preserved
        assert refreshed.name == "Original Name"
        assert refreshed.unit_fields.race == Race.HUMAN
        assert refreshed.unit_fields.player_class == PlayerClass.WARRIOR
        assert refreshed.unit_fields.faction == Faction.ALLIANCE
