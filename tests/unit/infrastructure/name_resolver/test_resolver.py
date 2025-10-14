"""Tests for the name resolver."""

import pytest
from icecap.infrastructure.name_resolver.resolver import ConcreteNameResolver
from icecap.infrastructure.driver.offsets import (
    UNIT_NAMEBLOCK_OFFSET,
    UNIT_NAMEBLOCK_NAME_OFFSET,
)
from icecap.infrastructure.name_resolver.offsets import (
    NAME_STORE_BASE,
    NAME_MASK_OFFSET,
    NAME_TABLE_ADDRESS_OFFSET,
)
from icecap.domain.models import Entity
from icecap.domain.enums import EntityType
from tests.utils import MockMemoryManager, MemoryBuilder


class TestNameResolverInitialization:
    """Test name resolver initialization."""

    def test_create_resolver_with_memory_manager(self):
        """Test creating a name resolver."""
        memory = MockMemoryManager()
        resolver = ConcreteNameResolver(memory)

        assert resolver.memory_manager is memory
        assert resolver.data_mapping_filename is None

    def test_create_resolver_with_custom_mapping_file(self):
        """Test creating resolver with custom mapping file."""
        memory = MockMemoryManager()
        resolver = ConcreteNameResolver(memory, data_mapping_filename="custom.csv")

        assert resolver.data_mapping_filename == "custom.csv"


class TestNameResolverUnitNames:
    """Test resolving unit names from memory."""

    def test_resolve_unit_name_success(self):
        """Test successfully resolving a unit name."""
        entity = Entity(
            guid=0x0F00000000000001,
            object_address=0x20000000,
            entity_type=EntityType.UNIT,
        )

        # Mock unit name in memory
        nameblock_address = 0x30000000
        name_address = 0x40000000
        name_bytes = b"Boar\x00"

        memory = (
            MemoryBuilder()
            .with_uint_at(
                0x20000000 + UNIT_NAMEBLOCK_OFFSET, nameblock_address
            )  # Nameblock pointer
            .with_uint_at(
                nameblock_address + UNIT_NAMEBLOCK_NAME_OFFSET, name_address
            )  # Name pointer
            .with_bytes_at(name_address, name_bytes)  # Actual name
            .build()
        )

        resolver = ConcreteNameResolver(memory)

        name = resolver.resolve_name(entity)

        assert name == "Boar"

    def test_resolve_unit_name_null_nameblock(self):
        """Test resolving unit name when nameblock is null."""
        entity = Entity(
            guid=0x0F00000000000001,
            object_address=0x20000000,
            entity_type=EntityType.UNIT,
        )

        memory = (
            MemoryBuilder().with_uint_at(0x20000000 + UNIT_NAMEBLOCK_OFFSET, 0).build()
        )  # Null nameblock

        resolver = ConcreteNameResolver(memory)

        name = resolver.resolve_name(entity)

        assert name == "Unknown Unit"

    def test_resolve_unit_name_null_name_address(self):
        """Test resolving unit name when name address is null."""
        entity = Entity(
            guid=0x0F00000000000001,
            object_address=0x20000000,
            entity_type=EntityType.UNIT,
        )

        nameblock_address = 0x30000000
        memory = (
            MemoryBuilder()
            .with_uint_at(0x20000000 + UNIT_NAMEBLOCK_OFFSET, nameblock_address)
            .with_uint_at(nameblock_address + UNIT_NAMEBLOCK_NAME_OFFSET, 0)  # Null name address
            .build()
        )

        resolver = ConcreteNameResolver(memory)

        name = resolver.resolve_name(entity)

        assert name == "Unknown Unit"

    def test_resolve_unit_name_exception_handling(self):
        """Test that exceptions during unit name resolution are handled."""
        entity = Entity(
            guid=0x0F00000000000001,
            object_address=0x20000000,
            entity_type=EntityType.UNIT,
        )

        memory = MockMemoryManager()  # Empty memory will cause read errors

        resolver = ConcreteNameResolver(memory)

        name = resolver.resolve_name(entity)

        assert name == "Unknown Unit"


class TestNameResolverPlayerNames:
    """Test resolving player names from memory."""

    def test_resolve_player_name_success(self):
        """Test successfully resolving a player name."""
        entity = Entity(
            guid=0x0F00000000000001,
            object_address=0x20000000,
            entity_type=EntityType.PLAYER,
        )

        # Player name resolution uses a hash table
        short_guid = 0x00000001
        mask = 0x000000FF
        index = mask & short_guid  # 1

        name_base_address = 0x50000000
        current_node_address = 0x60000000

        name_bytes = b"PlayerOne\x00"

        memory = (
            MemoryBuilder()
            # Mask and name table base
            .with_uint_at(NAME_STORE_BASE + NAME_MASK_OFFSET, mask)
            .with_uint_at(NAME_STORE_BASE + NAME_TABLE_ADDRESS_OFFSET, name_base_address)
            # Bucket data (12 bytes per bucket)
            .with_uint_at(name_base_address + (index * 12), 0)  # next_node_offset
            .with_uint_at(name_base_address + (index * 12) + 4, 0)  # padding
            .with_uint_at(
                name_base_address + (index * 12) + 8, current_node_address
            )  # current_node
            # Node data
            .with_uint_at(current_node_address, short_guid)  # Node GUID matches
            .with_bytes_at(current_node_address + 0x20, name_bytes)  # Name at offset
            .build()
        )

        resolver = ConcreteNameResolver(memory)

        name = resolver.resolve_name(entity)

        assert name == "PlayerOne"

    def test_resolve_player_name_not_found(self):
        """Test resolving player name when player is not in hash table."""
        entity = Entity(
            guid=0x0F00000000000001,
            object_address=0x20000000,
            entity_type=EntityType.PLAYER,
        )

        memory = (
            MemoryBuilder()
            .with_uint_at(NAME_STORE_BASE + NAME_MASK_OFFSET, 0xFF)
            .with_uint_at(NAME_STORE_BASE + NAME_TABLE_ADDRESS_OFFSET, 0x50000000)
            .with_uint_at(0x50000000 + (1 * 12) + 8, 0)  # No node
            .build()
        )

        resolver = ConcreteNameResolver(memory)

        name = resolver.resolve_name(entity)

        assert name == "Unknown Player"

    def test_resolve_player_name_null_mask(self):
        """Test resolving player name when mask is null."""
        entity = Entity(
            guid=0x0F00000000000001,
            object_address=0x20000000,
            entity_type=EntityType.PLAYER,
        )

        memory = (
            MemoryBuilder().with_uint_at(NAME_STORE_BASE + NAME_MASK_OFFSET, 0).build()
        )  # Mask is 0

        resolver = ConcreteNameResolver(memory)

        name = resolver.resolve_name(entity)

        assert name == "Unknown Player"

    def test_resolve_player_name_respects_max_reads(self):
        """Test that player name resolution respects max_name_reads limit."""
        entity = Entity(
            guid=0x0F00000000000001,
            object_address=0x20000000,
            entity_type=EntityType.PLAYER,
        )

        # Create a circular linked list that would loop forever
        memory = (
            MemoryBuilder()
            .with_uint_at(NAME_STORE_BASE + NAME_MASK_OFFSET, 0xFF)
            .with_uint_at(NAME_STORE_BASE + NAME_TABLE_ADDRESS_OFFSET, 0x50000000)
            .with_uint_at(0x50000000 + 8, 0x60000000)  # Node address
            .with_uint_at(0x60000000, 0x99999999)  # Wrong GUID
            .with_uint_at(0x60000000 + 4, 0)  # Next offset
            .with_uint_at(0x60000004, 0x60000000)  # Points to itself (circular)
            .build()
        )

        resolver = ConcreteNameResolver(memory)

        # Should not hang, should return "Unknown Player" after hitting limit
        name = resolver.resolve_name(entity)

        assert name == "Unknown Player"


class TestNameResolverGameObjectNames:
    """Test resolving game object names from CSV data."""

    def test_resolve_game_object_name_by_entry_id(self, gameobject_template_data_path: str):
        """Test resolving game object name by entry ID."""
        memory = MockMemoryManager()
        resolver = ConcreteNameResolver(memory, data_mapping_filename=gameobject_template_data_path)

        name = resolver.resolve_game_object_name_by_entry_id(4)

        assert name == "Bonfire Damage"

    def test_resolve_game_object_name_by_display_id(self, gameobject_template_data_path: str):
        """Test resolving game object name by display ID."""
        memory = MockMemoryManager()
        resolver = ConcreteNameResolver(memory, data_mapping_filename=gameobject_template_data_path)

        name = resolver.resolve_game_object_name_by_display_id(1)

        assert name == "Bonfire Damage"

    def test_resolve_game_object_name_by_unknown_entry_id(self, gameobject_template_data_path: str):
        """Test resolving game object name by entry ID."""
        memory = MockMemoryManager()
        resolver = ConcreteNameResolver(memory, data_mapping_filename=gameobject_template_data_path)

        name = resolver.resolve_game_object_name_by_entry_id(44)

        assert name == "Unknown Game Object"

    def test_game_object_name_file_not_found(self):
        """Test handling when game object CSV file doesn't exist."""
        memory = MockMemoryManager()
        resolver = ConcreteNameResolver(memory, data_mapping_filename="nonexistent.csv")

        name = resolver.resolve_game_object_name_by_entry_id(4)

        assert name == "Unknown Game Object"


class TestNameResolverLRUCaching:
    """Test LRU caching functionality."""

    def test_lru_cache_for_game_object_names(self, gameobject_template_data_path: str):
        """Test that LRU cache works for game object names."""
        memory = MockMemoryManager()
        resolver = ConcreteNameResolver(memory, data_mapping_filename=gameobject_template_data_path)

        # Call multiple times with same entry ID
        for _ in range(100):
            name = resolver.resolve_game_object_name_by_entry_id(4)
            assert name == "Bonfire Damage"

        # CSV should only be read once due to caching
        assert resolver.resolve_game_object_name_by_entry_id.cache_info().hits == 99

    def test_lru_cache_for_unit_names(self):
        """Test that LRU cache works for unit names."""
        entity = Entity(
            guid=0x0F00000000000001,
            object_address=0x20000000,
            entity_type=EntityType.UNIT,
        )

        nameblock_address = 0x30000000
        name_address = 0x40000000
        name_bytes = b"Boar\x00"

        memory = (
            MemoryBuilder()
            .with_uint_at(0x20000000 + UNIT_NAMEBLOCK_OFFSET, nameblock_address)
            .with_uint_at(nameblock_address + UNIT_NAMEBLOCK_NAME_OFFSET, name_address)
            .with_bytes_at(name_address, name_bytes)
            .build()
        )

        resolver = ConcreteNameResolver(memory)

        # Call multiple times with same entity
        for _ in range(10):
            name = resolver.resolve_name(entity)
            assert name == "Boar"

        # Should have cache hits
        assert resolver.resolve_name.cache_info().hits > 5


class TestNameResolverEdgeCases:
    """Test edge cases in name resolution."""

    def test_resolve_unsupported_entity_type(self):
        """Test resolving name for unsupported entity type."""
        entity = Entity(
            guid=0x0F00000000000001,
            object_address=0x20000000,
            entity_type=EntityType.ITEM,
        )

        memory = MockMemoryManager()
        resolver = ConcreteNameResolver(memory)

        with pytest.raises(NotImplementedError, match="Name resolution for"):
            resolver.resolve_name(entity)

    def test_resolve_game_object_raises_error(self):
        """Test that resolving game object via resolve_name raises error."""
        entity = Entity(
            guid=0x0F00000000000001,
            object_address=0x20000000,
            entity_type=EntityType.GAME_OBJECT,
        )

        memory = MockMemoryManager()
        resolver = ConcreteNameResolver(memory)

        with pytest.raises(ValueError, match="Use resolve_game_object_name_by_entry_id"):
            resolver.resolve_name(entity)
