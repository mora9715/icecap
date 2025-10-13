"""Test mixins for IceCap tests."""

from icecap.domain.models import Entity
from icecap.domain.enums import EntityType
from icecap.domain.dto import Position


class AssertionsMixin:
    """Common assertions for domain objects."""

    def assert_entity_valid(self, entity: Entity):
        """Assert an entity is valid."""
        assert entity.guid > 0, "GUID must be positive"
        assert entity.object_address > 0, "Object address must be positive"
        assert isinstance(entity.entity_type, EntityType), "Entity type must be EntityType"

    def assert_position_valid(self, position: Position):
        """Assert a position is valid."""
        assert isinstance(position.x, (int, float)), "X must be numeric"
        assert isinstance(position.y, (int, float)), "Y must be numeric"
        assert isinstance(position.z, (int, float)), "Z must be numeric"
        assert isinstance(position.rotation, (int, float)), "Rotation must be numeric"


class DataFactoryMixin:
    """Factory methods for creating test data."""

    @staticmethod
    def create_entity(
        guid: int = 1, address: int = 0x1000, entity_type: EntityType = EntityType.PLAYER
    ):
        """Create a test Entity."""
        return Entity(guid=guid, object_address=address, entity_type=entity_type)

    @staticmethod
    def create_position(x: float = 0.0, y: float = 0.0, z: float = 0.0, rotation: float = 0.0):
        """Create a test Position."""
        return Position(x=x, y=y, z=z, rotation=rotation)
