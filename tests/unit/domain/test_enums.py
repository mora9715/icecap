"""Tests for domain enums."""

from icecap.domain.enums import EntityType, Faction, Race, Gender, PlayerClass


class TestEntityType:
    """Tests for EntityType enum."""

    def test_entity_type_values(self):
        """Test that all entity types have correct values."""
        assert EntityType.PLAYER is not None
        assert EntityType.UNIT is not None
        assert EntityType.GAME_OBJECT is not None

    def test_entity_type_comparison(self):
        """Test entity type equality comparison."""
        assert EntityType.PLAYER == EntityType.PLAYER
        assert EntityType.PLAYER != EntityType.UNIT
        assert EntityType.UNIT != EntityType.GAME_OBJECT

    def test_entity_type_is_enum(self):
        """Test that EntityType is an enum."""
        from enum import Enum

        assert issubclass(EntityType, Enum)


class TestFaction:
    """Tests for Faction enum."""

    def test_faction_values(self):
        """Test that all factions exist."""
        assert Faction.ALLIANCE is not None
        assert Faction.HORDE is not None

    def test_faction_comparison(self):
        """Test faction equality comparison."""
        assert Faction.ALLIANCE == Faction.ALLIANCE
        assert Faction.HORDE == Faction.HORDE
        assert Faction.ALLIANCE != Faction.HORDE

    def test_faction_is_enum(self):
        """Test that Faction is an enum."""
        from enum import Enum

        assert issubclass(Faction, Enum)


class TestRace:
    """Tests for Race enum."""

    def test_race_values_exist(self):
        """Test that common races exist."""
        # Alliance races
        assert Race.HUMAN is not None
        assert Race.DWARF is not None
        assert Race.NIGHT_ELF is not None
        assert Race.GNOME is not None
        assert Race.DRAENEI is not None

        # Horde races
        assert Race.ORC is not None
        assert Race.UNDEAD is not None
        assert Race.TAUREN is not None
        assert Race.TROLL is not None
        assert Race.BLOOD_ELF is not None

    def test_race_comparison(self):
        """Test race equality comparison."""
        assert Race.HUMAN == Race.HUMAN
        assert Race.ORC == Race.ORC
        assert Race.HUMAN != Race.ORC

    def test_race_is_enum(self):
        """Test that Race is an enum."""
        from enum import Enum

        assert issubclass(Race, Enum)


class TestGender:
    """Tests for Gender enum."""

    def test_gender_values(self):
        """Test that all genders exist."""
        assert Gender.MALE is not None
        assert Gender.FEMALE is not None

    def test_gender_comparison(self):
        """Test gender equality comparison."""
        assert Gender.MALE == Gender.MALE
        assert Gender.FEMALE == Gender.FEMALE
        assert Gender.MALE != Gender.FEMALE

    def test_gender_is_enum(self):
        """Test that Gender is an enum."""
        from enum import Enum

        assert issubclass(Gender, Enum)


class TestPlayerClass:
    """Tests for PlayerClass enum."""

    def test_player_class_values_exist(self):
        """Test that all player classes exist."""
        assert PlayerClass.WARRIOR is not None
        assert PlayerClass.PALADIN is not None
        assert PlayerClass.HUNTER is not None
        assert PlayerClass.ROGUE is not None
        assert PlayerClass.PRIEST is not None
        assert PlayerClass.DEATH_KNIGHT is not None
        assert PlayerClass.SHAMAN is not None
        assert PlayerClass.MAGE is not None
        assert PlayerClass.WARLOCK is not None
        assert PlayerClass.DRUID is not None

    def test_player_class_comparison(self):
        """Test player class equality comparison."""
        assert PlayerClass.WARRIOR == PlayerClass.WARRIOR
        assert PlayerClass.MAGE == PlayerClass.MAGE
        assert PlayerClass.WARRIOR != PlayerClass.MAGE

    def test_player_class_is_enum(self):
        """Test that PlayerClass is an enum."""
        from enum import Enum

        assert issubclass(PlayerClass, Enum)

    def test_all_classes_unique(self):
        """Test that all player classes are unique."""
        classes = [
            PlayerClass.WARRIOR,
            PlayerClass.PALADIN,
            PlayerClass.HUNTER,
            PlayerClass.ROGUE,
            PlayerClass.PRIEST,
            PlayerClass.DEATH_KNIGHT,
            PlayerClass.SHAMAN,
            PlayerClass.MAGE,
            PlayerClass.WARLOCK,
            PlayerClass.DRUID,
        ]
        assert len(classes) == len(set(classes))
