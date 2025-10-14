import struct
from icecap.infrastructure.driver.object_manager import ObjectManager
from icecap.infrastructure.driver.offsets import (
    LOCAL_PLAYER_GUID_OFFSET,
    FIRST_OBJECT_OFFSET,
    OBJECT_TYPE_OFFSET,
    OBJECT_GUID_OFFSET,
    NEXT_OBJECT_OFFSET,
    MAP_ID_OFFSET,
    UNIT_X_POSITION_OFFSET,
    GAME_OBJECT_X_POSITION_OFFSET,
    OBJECT_FIELDS_OFFSET,
)
from icecap.domain.enums import EntityType
from icecap.domain.models import Entity
from tests.utils import MockMemoryManager, MemoryBuilder


class TestObjectManagerInitialization:
    """Test ObjectManager initialization."""

    def test_create_object_manager(self):
        """Test creating an object manager."""
        memory = MockMemoryManager()
        address = 0x12345678

        obj_mgr = ObjectManager(memory, address)

        assert obj_mgr.memory_manager is memory
        assert obj_mgr.address == address
        assert obj_mgr.max_objects == 1000  # Default value

    def test_create_object_manager_with_custom_max_objects(self):
        """Test creating object manager with custom max_objects."""
        memory = MockMemoryManager()

        obj_mgr = ObjectManager(memory, 0x12345678, max_objects=500)

        assert obj_mgr.max_objects == 500


class TestObjectManagerGetLocalPlayerGuid:
    """Test getting local player GUID from object manager."""

    def test_get_local_player_guid(self):
        """Test retrieving local player GUID."""
        guid = 0x0F00000000001234
        memory = (
            MemoryBuilder().with_ulonglong_at(0x12345678 + LOCAL_PLAYER_GUID_OFFSET, guid).build()
        )

        obj_mgr = ObjectManager(memory, 0x12345678)

        result = obj_mgr.get_local_player_guid()

        assert result == guid

    def test_get_local_player_guid_zero(self):
        """Test retrieving local player GUID when player not in game."""
        memory = MemoryBuilder().with_ulonglong_at(0x12345678 + LOCAL_PLAYER_GUID_OFFSET, 0).build()

        obj_mgr = ObjectManager(memory, 0x12345678)

        result = obj_mgr.get_local_player_guid()

        assert result == 0


class TestObjectManagerYieldObjects:
    """Test yielding objects from object manager."""

    def test_yield_single_object(self):
        """Test yielding a single object."""
        # Object at address 0x20000000
        memory = (
            MemoryBuilder()
            .with_uint_at(0x12345678 + FIRST_OBJECT_OFFSET, 0x20000000)  # First object address
            .with_uint_at(0x20000000 + OBJECT_TYPE_OFFSET, EntityType.UNIT.value)  # Object type
            .with_ulonglong_at(0x20000000 + OBJECT_GUID_OFFSET, 0x0F00000000000001)  # Object GUID
            .with_uint_at(0x20000000 + NEXT_OBJECT_OFFSET, 0)  # Next object (null)
            .build()
        )

        obj_mgr = ObjectManager(memory, 0x12345678)

        objects = list(obj_mgr.yield_objects())

        assert len(objects) == 1
        assert objects[0].guid == 0x0F00000000000001
        assert objects[0].object_address == 0x20000000
        assert objects[0].entity_type == EntityType.UNIT

    def test_yield_multiple_objects(self):
        """Test yielding multiple objects."""
        memory = (
            MemoryBuilder()
            # First object
            .with_uint_at(0x12345678 + FIRST_OBJECT_OFFSET, 0x20000000)
            .with_uint_at(0x20000000 + OBJECT_TYPE_OFFSET, EntityType.UNIT.value)
            .with_ulonglong_at(0x20000000 + OBJECT_GUID_OFFSET, 0x0F00000000000001)
            .with_uint_at(0x20000000 + NEXT_OBJECT_OFFSET, 0x20001000)  # Next object
            # Second object
            .with_uint_at(0x20001000 + OBJECT_TYPE_OFFSET, EntityType.PLAYER.value)
            .with_ulonglong_at(0x20001000 + OBJECT_GUID_OFFSET, 0x0F00000000000002)
            .with_uint_at(0x20001000 + NEXT_OBJECT_OFFSET, 0x20002000)  # Next object
            # Third object
            .with_uint_at(0x20002000 + OBJECT_TYPE_OFFSET, EntityType.GAME_OBJECT.value)
            .with_ulonglong_at(0x20002000 + OBJECT_GUID_OFFSET, 0x0F00000000000003)
            .with_uint_at(0x20002000 + NEXT_OBJECT_OFFSET, 0)  # Next object (null)
            .build()
        )

        obj_mgr = ObjectManager(memory, 0x12345678)

        objects = list(obj_mgr.yield_objects())

        assert len(objects) == 3
        assert objects[0].entity_type == EntityType.UNIT
        assert objects[1].entity_type == EntityType.PLAYER
        assert objects[2].entity_type == EntityType.GAME_OBJECT

    def test_yield_objects_respects_max_objects(self):
        """Test that yielding objects respects max_objects limit."""
        # Create a chain of 10 objects
        memory_builder = MemoryBuilder().with_uint_at(0x12345678 + FIRST_OBJECT_OFFSET, 0x20000000)

        for i in range(10):
            obj_addr = 0x20000000 + (i * 0x1000)
            next_addr = 0x20000000 + ((i + 1) * 0x1000) if i < 9 else 0

            memory_builder.with_uint_at(obj_addr + OBJECT_TYPE_OFFSET, EntityType.UNIT.value)
            memory_builder.with_ulonglong_at(obj_addr + OBJECT_GUID_OFFSET, 0x0F00000000000000 + i)
            memory_builder.with_uint_at(obj_addr + NEXT_OBJECT_OFFSET, next_addr)

        memory = memory_builder.build()

        # Set max_objects to 5
        obj_mgr = ObjectManager(memory, 0x12345678, max_objects=5)

        objects = list(obj_mgr.yield_objects())

        # Should only yield 5 objects
        assert len(objects) == 5

    def test_yield_objects_handles_invalid_type(self):
        """Test that yielding objects stops on invalid entity type."""
        memory = (
            MemoryBuilder()
            .with_uint_at(0x12345678 + FIRST_OBJECT_OFFSET, 0x20000000)
            .with_uint_at(0x20000000 + OBJECT_TYPE_OFFSET, 999)  # Invalid entity type
            .with_ulonglong_at(0x20000000 + OBJECT_GUID_OFFSET, 0x0F00000000000001)
            .with_uint_at(0x20000000 + NEXT_OBJECT_OFFSET, 0)
            .build()
        )

        obj_mgr = ObjectManager(memory, 0x12345678)

        objects = list(obj_mgr.yield_objects())

        # Should stop when encountering invalid type
        assert len(objects) == 0

    def test_yield_objects_empty_list(self):
        """Test yielding objects when no objects exist."""
        memory = (
            MemoryBuilder().with_uint_at(0x12345678 + FIRST_OBJECT_OFFSET, 0).build()
        )  # First object is null

        obj_mgr = ObjectManager(memory, 0x12345678)

        objects = list(obj_mgr.yield_objects())

        assert len(objects) == 0


class TestObjectManagerGetEntityPosition:
    """Test getting entity position."""

    def test_get_unit_position(self):
        """Test getting position of a unit entity."""
        entity = Entity(
            guid=0x0F00000000000001,
            object_address=0x20000000,
            entity_type=EntityType.UNIT,
        )

        # Position: y=1.5, x=2.5, z=3.5, padding=0.0, rotation=1.57
        position_data = struct.pack("<fffff", 1.5, 2.5, 3.5, 0.0, 1.57)
        memory = (
            MemoryBuilder()
            .with_bytes_at(0x20000000 + UNIT_X_POSITION_OFFSET, position_data)
            .build()
        )

        obj_mgr = ObjectManager(memory, 0x12345678)

        position = obj_mgr.get_entity_position(entity)

        assert abs(position.y - 1.5) < 0.01
        assert abs(position.x - 2.5) < 0.01
        assert abs(position.z - 3.5) < 0.01
        assert abs(position.rotation - 1.57) < 0.01

    def test_get_game_object_position(self):
        """Test getting position of a game object entity."""
        entity = Entity(
            guid=0x0F00000000000001,
            object_address=0x20000000,
            entity_type=EntityType.GAME_OBJECT,
        )

        position_data = struct.pack("<fffff", 10.0, 20.0, 30.0, 0.0, 3.14)
        memory = (
            MemoryBuilder()
            .with_bytes_at(0x20000000 + GAME_OBJECT_X_POSITION_OFFSET, position_data)
            .build()
        )

        obj_mgr = ObjectManager(memory, 0x12345678)

        position = obj_mgr.get_entity_position(entity)

        assert abs(position.y - 10.0) < 0.01
        assert abs(position.x - 20.0) < 0.01
        assert abs(position.z - 30.0) < 0.01
        assert abs(position.rotation - 3.14) < 0.01

    def test_get_player_position(self):
        """Test getting position of a player entity."""
        entity = Entity(
            guid=0x0F00000000000001,
            object_address=0x20000000,
            entity_type=EntityType.PLAYER,
        )

        position_data = struct.pack("<fffff", 5.5, 15.5, 25.5, 0.0, 0.0)
        memory = (
            MemoryBuilder()
            .with_bytes_at(0x20000000 + UNIT_X_POSITION_OFFSET, position_data)
            .build()
        )

        obj_mgr = ObjectManager(memory, 0x12345678)

        position = obj_mgr.get_entity_position(entity)

        assert abs(position.y - 5.5) < 0.01
        assert abs(position.x - 15.5) < 0.01
        assert abs(position.z - 25.5) < 0.01


class TestObjectManagerGetUnitFields:
    """Test getting unit fields."""

    def test_get_unit_fields(self):
        """Test retrieving unit fields from memory."""
        entity = Entity(
            guid=0x0F00000000000001,
            object_address=0x20000000,
            entity_type=EntityType.UNIT,
        )

        # Mock unit fields pointer and data
        fields_address = 0x30000000
        memory = (
            MemoryBuilder()
            .with_uint_at(0x20000000 + 0x8, fields_address)  # Fields pointer
            # First few fields of UnitFields
            .with_ulonglong_at(fields_address, 0x0F00000000000001)  # guid
            .with_uint_at(fields_address + 8, 1)  # type
            .with_uint_at(fields_address + 12, 12345)  # entry
            .with_uint_at(fields_address + 16, 100)  # scale_x
            # Skip to health/level fields (approximate offsets)
            .with_uint_at(fields_address + 100, 1500)  # health
            .with_uint_at(fields_address + 200, 60)  # level
            .with_uint_at(fields_address + 104, 2000)  # max_health
            .build()
        )

        obj_mgr = ObjectManager(memory, 0x12345678)

        unit_fields = obj_mgr.get_unit_fields(entity)

        assert unit_fields.guid == 0x0F00000000000001
        assert unit_fields.entry == 12345


class TestObjectManagerGetGameObjectFields:
    """Test getting game object fields."""

    def test_get_game_object_fields(self):
        """Test retrieving game object fields from memory."""
        entity = Entity(
            guid=0x0F00000000000001,
            object_address=0x20000000,
            entity_type=EntityType.GAME_OBJECT,
        )

        fields_address = 0x30000000
        memory = (
            MemoryBuilder()
            .with_uint_at(0x20000000 + OBJECT_FIELDS_OFFSET, fields_address)  # Fields pointer
            # GameObjectFields structure
            .with_ulonglong_at(fields_address, 0x0F00000000000001)  # guid
            .with_uint_at(fields_address + 8, 5)  # type
            .with_uint_at(fields_address + 12, 54321)  # entry
            .with_uint_at(fields_address + 16, 100)  # scale_x
            .with_uint_at(fields_address + 20, 0)  # padding
            .with_ulonglong_at(fields_address + 24, 0x0F00000000000002)  # created_by
            .with_uint_at(fields_address + 32, 999)  # display_id
            .build()
        )

        obj_mgr = ObjectManager(memory, 0x12345678)

        go_fields = obj_mgr.get_game_object_fields(entity)

        assert go_fields.guid == 0x0F00000000000001
        assert go_fields.entry == 54321
        assert go_fields.display_id == 999
        assert go_fields.created_by == 0x0F00000000000002


class TestObjectManagerGetMapId:
    """Test getting map ID."""

    def test_get_map_id(self):
        """Test retrieving current map ID."""
        map_id = 0  # Eastern Kingdoms
        memory = MemoryBuilder().with_uint_at(0x12345678 + MAP_ID_OFFSET, map_id).build()

        obj_mgr = ObjectManager(memory, 0x12345678)

        result = obj_mgr.get_map_id()

        assert result == map_id

    def test_get_different_map_ids(self):
        """Test retrieving different map IDs."""
        test_map_ids = [0, 1, 530, 571]  # EK, Kalimdor, Outland, Northrend

        for map_id in test_map_ids:
            memory = MemoryBuilder().with_uint_at(0x12345678 + MAP_ID_OFFSET, map_id).build()
            obj_mgr = ObjectManager(memory, 0x12345678)

            result = obj_mgr.get_map_id()
            assert result == map_id
