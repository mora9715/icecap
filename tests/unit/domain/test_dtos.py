"""Tests for domain DTOs (Data Transfer Objects)."""

import pytest
from icecap.domain.dto import Position, GameObjectFields, UnitFields
from icecap.domain.enums import Race, Gender, PlayerClass, Faction


class TestPosition:
    """Tests for Position DTO."""

    def test_position_creation(self):
        """Test basic position creation."""
        # Arrange & Act
        position = Position(x=100.0, y=200.0, z=300.0, rotation=1.5)

        # Assert
        assert position.x == 100.0
        assert position.y == 200.0
        assert position.z == 300.0
        assert position.rotation == 1.5

    def test_position_with_integers(self):
        """Test position creation with integer values."""
        # Arrange & Act
        position = Position(x=100, y=200, z=300, rotation=0)

        # Assert
        assert position.x == 100
        assert position.y == 200
        assert position.z == 300
        assert position.rotation == 0

    def test_position_with_negative_values(self):
        """Test position with negative coordinates."""
        # Arrange & Act
        position = Position(x=-50.5, y=-100.0, z=-25.75, rotation=-3.14)

        # Assert
        assert position.x == -50.5
        assert position.y == -100.0
        assert position.z == -25.75
        assert position.rotation == -3.14

    def test_position_with_zero_values(self):
        """Test position at origin."""
        # Arrange & Act
        position = Position(x=0.0, y=0.0, z=0.0, rotation=0.0)

        # Assert
        assert position.x == 0.0
        assert position.y == 0.0
        assert position.z == 0.0
        assert position.rotation == 0.0

    def test_position_is_immutable(self):
        """Test that position is frozen (immutable)."""
        # Arrange
        position = Position(x=100.0, y=200.0, z=300.0, rotation=1.5)

        # Act & Assert
        with pytest.raises(Exception):
            position.x = 999.0

    def test_position_equality(self):
        """Test position equality comparison."""
        # Arrange
        pos1 = Position(x=100.0, y=200.0, z=300.0, rotation=1.5)
        pos2 = Position(x=100.0, y=200.0, z=300.0, rotation=1.5)
        pos3 = Position(x=101.0, y=200.0, z=300.0, rotation=1.5)

        # Assert
        assert pos1 == pos2
        assert pos1 != pos3


class TestGameObjectFields:
    """Tests for GameObjectFields DTO."""

    def test_game_object_fields_creation(self):
        """Test basic game object fields creation."""
        # Arrange & Act
        fields = GameObjectFields(entry_id=1234, display_id=5678, owner_guid=9999, state=1)

        # Assert
        assert fields.entry_id == 1234
        assert fields.display_id == 5678
        assert fields.owner_guid == 9999
        assert fields.state == 1

    def test_game_object_fields_with_zero_owner(self):
        """Test game object fields with no owner."""
        # Arrange & Act
        fields = GameObjectFields(entry_id=1234, display_id=5678, owner_guid=0, state=0)

        # Assert
        assert fields.owner_guid == 0
        assert fields.state == 0

    def test_game_object_fields_is_immutable(self):
        """Test that game object fields is frozen (immutable)."""
        # Arrange
        fields = GameObjectFields(entry_id=1234, display_id=5678, owner_guid=9999, state=1)

        # Act & Assert
        with pytest.raises(Exception):
            fields.entry_id = 4321

    def test_game_object_fields_equality(self):
        """Test game object fields equality comparison."""
        # Arrange
        fields1 = GameObjectFields(entry_id=1234, display_id=5678, owner_guid=9999, state=1)
        fields2 = GameObjectFields(entry_id=1234, display_id=5678, owner_guid=9999, state=1)
        fields3 = GameObjectFields(entry_id=4321, display_id=5678, owner_guid=9999, state=1)

        # Assert
        assert fields1 == fields2
        assert fields1 != fields3


class TestUnitFields:
    """Tests for UnitFields DTO."""

    def test_unit_fields_creation(self):
        """Test basic unit fields creation."""
        # Arrange & Act
        fields = UnitFields(
            level=80,
            hit_points=5000,
            max_hit_points=6000,
            race=Race.HUMAN,
            gender=Gender.MALE,
            player_class=PlayerClass.WARRIOR,
            faction=Faction.ALLIANCE,
        )

        # Assert
        assert fields.race == Race.HUMAN
        assert fields.gender == Gender.MALE
        assert fields.player_class == PlayerClass.WARRIOR
        assert fields.level == 80
        assert fields.faction == Faction.ALLIANCE
        assert fields.hit_points == 5000
        assert fields.max_hit_points == 6000

    def test_unit_fields_minimal(self):
        """Test unit fields with only required fields."""
        # Arrange & Act
        fields = UnitFields(level=1, hit_points=100, max_hit_points=100)

        # Assert
        assert fields.level == 1
        assert fields.hit_points == 100
        assert fields.max_hit_points == 100
        assert fields.race is None
        assert fields.faction is None

    def test_unit_fields_low_health(self):
        """Test unit fields with low health."""
        # Arrange & Act
        fields = UnitFields(
            level=80,
            hit_points=100,  # Low HP
            max_hit_points=6000,
            race=Race.HUMAN,
            gender=Gender.MALE,
            player_class=PlayerClass.WARRIOR,
            faction=Faction.ALLIANCE,
        )

        # Assert
        assert fields.hit_points < fields.max_hit_points
        assert fields.hit_points == 100

    def test_unit_fields_full_health(self):
        """Test unit fields at full health."""
        # Arrange & Act
        fields = UnitFields(
            level=80,
            hit_points=6000,
            max_hit_points=6000,
            race=Race.HUMAN,
            gender=Gender.MALE,
            player_class=PlayerClass.WARRIOR,
            faction=Faction.ALLIANCE,
        )

        # Assert
        assert fields.hit_points == fields.max_hit_points

    def test_unit_fields_is_immutable(self):
        """Test that unit fields is frozen (immutable)."""
        # Arrange
        fields = UnitFields(
            level=80,
            hit_points=5000,
            max_hit_points=6000,
            race=Race.HUMAN,
            gender=Gender.MALE,
            player_class=PlayerClass.WARRIOR,
            faction=Faction.ALLIANCE,
        )

        # Act & Assert
        with pytest.raises(Exception):
            fields.level = 81

    def test_unit_fields_equality(self):
        """Test unit fields equality comparison."""
        # Arrange
        fields1 = UnitFields(
            level=80,
            hit_points=5000,
            max_hit_points=6000,
            race=Race.HUMAN,
            gender=Gender.MALE,
            player_class=PlayerClass.WARRIOR,
            faction=Faction.ALLIANCE,
        )
        fields2 = UnitFields(
            level=80,
            hit_points=5000,
            max_hit_points=6000,
            race=Race.HUMAN,
            gender=Gender.MALE,
            player_class=PlayerClass.WARRIOR,
            faction=Faction.ALLIANCE,
        )
        fields3 = UnitFields(
            level=80,
            hit_points=5000,
            max_hit_points=6000,
            race=Race.ORC,
            gender=Gender.MALE,
            player_class=PlayerClass.WARRIOR,
            faction=Faction.HORDE,
        )

        # Assert
        assert fields1 == fields2
        assert fields1 != fields3

    def test_unit_fields_different_classes(self):
        """Test unit fields with different player classes."""
        # Test multiple classes
        for player_class in [PlayerClass.WARRIOR, PlayerClass.MAGE, PlayerClass.ROGUE]:
            fields = UnitFields(
                level=80,
                hit_points=5000,
                max_hit_points=6000,
                race=Race.HUMAN,
                gender=Gender.MALE,
                player_class=player_class,
                faction=Faction.ALLIANCE,
            )
            assert fields.player_class == player_class
