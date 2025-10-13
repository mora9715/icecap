"""Tests for domain entity models."""

import pytest
from icecap.domain.models import Entity, Player, Unit, GameObject
from icecap.domain.enums import EntityType, Faction, Race, Gender, PlayerClass
from icecap.domain.dto import Position, UnitFields, GameObjectFields


class TestEntity:
    """Tests for Entity class."""

    def test_entity_creation(self):
        """Test basic entity creation."""
        # Arrange & Act
        entity = Entity(guid=12345, object_address=0x1000, entity_type=EntityType.PLAYER)

        # Assert
        assert entity.guid == 12345
        assert entity.object_address == 0x1000
        assert entity.entity_type == EntityType.PLAYER

    def test_entity_is_immutable(self):
        """Test that entity is frozen (immutable)."""
        # Arrange
        entity = Entity(guid=12345, object_address=0x1000, entity_type=EntityType.PLAYER)

        # Act & Assert
        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
            entity.guid = 99999

    def test_entity_with_different_types(self):
        """Test entity creation with different entity types."""
        # Test PLAYER
        player_entity = Entity(guid=1, object_address=0x1000, entity_type=EntityType.PLAYER)
        assert player_entity.entity_type == EntityType.PLAYER

        # Test UNIT
        unit_entity = Entity(guid=2, object_address=0x2000, entity_type=EntityType.UNIT)
        assert unit_entity.entity_type == EntityType.UNIT

        # Test GAME_OBJECT
        object_entity = Entity(guid=3, object_address=0x3000, entity_type=EntityType.GAME_OBJECT)
        assert object_entity.entity_type == EntityType.GAME_OBJECT

    def test_entity_equality(self):
        """Test entity equality comparison."""
        # Arrange
        entity1 = Entity(guid=123, object_address=0x1000, entity_type=EntityType.PLAYER)
        entity2 = Entity(guid=123, object_address=0x1000, entity_type=EntityType.PLAYER)
        entity3 = Entity(guid=456, object_address=0x1000, entity_type=EntityType.PLAYER)

        # Assert
        assert entity1 == entity2
        assert entity1 != entity3


class TestPlayer:
    """Tests for Player class."""

    def test_player_creation(self):
        """Test player creation with all fields."""
        # Arrange
        position = Position(x=100.0, y=200.0, z=300.0, rotation=1.5)
        unit_fields = UnitFields(
            level=80,
            hit_points=1000,
            max_hit_points=1500,
            race=Race.HUMAN,
            gender=Gender.MALE,
            player_class=PlayerClass.WARRIOR,
            faction=Faction.ALLIANCE,
        )

        # Act
        player = Player(
            guid=12345,
            object_address=0x1000,
            entity_type=EntityType.PLAYER,
            position=position,
            name="TestPlayer",
            unit_fields=unit_fields,
        )

        # Assert
        assert player.guid == 12345
        assert player.name == "TestPlayer"
        assert player.position == position
        assert player.unit_fields == unit_fields
        assert player.unit_fields.level == 80

    def test_player_is_enemy_same_faction(self):
        """Test that players of same faction are not enemies."""
        # Arrange
        position = Position(x=0.0, y=0.0, z=0.0, rotation=0.0)
        unit_fields_alliance = UnitFields(
            level=80,
            hit_points=1000,
            max_hit_points=1500,
            race=Race.HUMAN,
            gender=Gender.MALE,
            player_class=PlayerClass.WARRIOR,
            faction=Faction.ALLIANCE,
        )

        player1 = Player(
            guid=1,
            object_address=0x1000,
            entity_type=EntityType.PLAYER,
            position=position,
            name="Player1",
            unit_fields=unit_fields_alliance,
        )
        player2 = Player(
            guid=2,
            object_address=0x2000,
            entity_type=EntityType.PLAYER,
            position=position,
            name="Player2",
            unit_fields=unit_fields_alliance,
        )

        # Act & Assert
        assert not player1.is_enemy(player2)

    def test_player_is_enemy_different_faction(self):
        """Test that players of different factions are enemies."""
        # Arrange
        position = Position(x=0.0, y=0.0, z=0.0, rotation=0.0)

        unit_fields_alliance = UnitFields(
            level=80,
            hit_points=1000,
            max_hit_points=1500,
            race=Race.HUMAN,
            gender=Gender.MALE,
            player_class=PlayerClass.WARRIOR,
            faction=Faction.ALLIANCE,
        )
        unit_fields_horde = UnitFields(
            level=80,
            hit_points=1000,
            max_hit_points=1500,
            race=Race.ORC,
            gender=Gender.MALE,
            player_class=PlayerClass.WARRIOR,
            faction=Faction.HORDE,
        )

        player_alliance = Player(
            guid=1,
            object_address=0x1000,
            entity_type=EntityType.PLAYER,
            position=position,
            name="AlliancePlayer",
            unit_fields=unit_fields_alliance,
        )
        player_horde = Player(
            guid=2,
            object_address=0x2000,
            entity_type=EntityType.PLAYER,
            position=position,
            name="HordePlayer",
            unit_fields=unit_fields_horde,
        )

        # Act & Assert
        assert player_alliance.is_enemy(player_horde)
        assert player_horde.is_enemy(player_alliance)

    def test_player_is_immutable(self):
        """Test that player is frozen (immutable)."""
        # Arrange
        position = Position(x=100.0, y=200.0, z=300.0, rotation=1.5)
        unit_fields = UnitFields(
            level=80,
            hit_points=1000,
            max_hit_points=1500,
            race=Race.HUMAN,
            gender=Gender.MALE,
            player_class=PlayerClass.WARRIOR,
            faction=Faction.ALLIANCE,
        )
        player = Player(
            guid=12345,
            object_address=0x1000,
            entity_type=EntityType.PLAYER,
            position=position,
            name="TestPlayer",
            unit_fields=unit_fields,
        )

        # Act & Assert
        with pytest.raises(Exception):
            player.name = "NewName"


class TestUnit:
    """Tests for Unit class."""

    def test_unit_creation(self):
        """Test unit creation with all fields."""
        # Arrange
        position = Position(x=50.0, y=100.0, z=150.0, rotation=0.5)
        unit_fields = UnitFields(
            level=60,
            hit_points=800,
            max_hit_points=1200,
            race=Race.ORC,
            gender=Gender.FEMALE,
            player_class=PlayerClass.MAGE,
            faction=Faction.HORDE,
        )

        # Act
        unit = Unit(
            guid=54321,
            object_address=0x2000,
            entity_type=EntityType.UNIT,
            position=position,
            name="TestNPC",
            unit_fields=unit_fields,
        )

        # Assert
        assert unit.guid == 54321
        assert unit.name == "TestNPC"
        assert unit.position == position
        assert unit.unit_fields == unit_fields
        assert unit.unit_fields.level == 60

    def test_unit_is_immutable(self):
        """Test that unit is frozen (immutable)."""
        # Arrange
        position = Position(x=50.0, y=100.0, z=150.0, rotation=0.5)
        unit_fields = UnitFields(
            level=60,
            hit_points=800,
            max_hit_points=1200,
            race=Race.ORC,
            gender=Gender.FEMALE,
            player_class=PlayerClass.MAGE,
            faction=Faction.HORDE,
        )
        unit = Unit(
            guid=54321,
            object_address=0x2000,
            entity_type=EntityType.UNIT,
            position=position,
            name="TestNPC",
            unit_fields=unit_fields,
        )

        # Act & Assert
        with pytest.raises(Exception):
            unit.name = "NewName"


class TestGameObject:
    """Tests for GameObject class."""

    def test_game_object_creation(self):
        """Test game object creation with all fields."""
        # Arrange
        position = Position(x=25.0, y=75.0, z=125.0, rotation=2.0)
        game_object_fields = GameObjectFields(entry_id=1234, display_id=5678, owner_guid=0, state=1)

        # Act
        game_object = GameObject(
            guid=99999,
            object_address=0x3000,
            entity_type=EntityType.GAME_OBJECT,
            position=position,
            name="TestChest",
            game_object_fields=game_object_fields,
        )

        # Assert
        assert game_object.guid == 99999
        assert game_object.name == "TestChest"
        assert game_object.position == position
        assert game_object.game_object_fields == game_object_fields
        assert game_object.game_object_fields.entry_id == 1234

    def test_game_object_is_immutable(self):
        """Test that game object is frozen (immutable)."""
        # Arrange
        position = Position(x=25.0, y=75.0, z=125.0, rotation=2.0)
        game_object_fields = GameObjectFields(entry_id=1234, display_id=5678, owner_guid=0, state=1)
        game_object = GameObject(
            guid=99999,
            object_address=0x3000,
            entity_type=EntityType.GAME_OBJECT,
            position=position,
            name="TestChest",
            game_object_fields=game_object_fields,
        )

        # Act & Assert
        with pytest.raises(Exception):
            game_object.name = "NewName"
