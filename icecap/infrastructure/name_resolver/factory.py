"""Factory for creating name resolver instances."""

from icecap.infrastructure.memory_manager import MemoryManager
from .resolver import ConcreteNameResolver
from .interface import NameResolver


def get_name_resolver(
    memory_manager: MemoryManager, data_mapping_filename: str | None = None
) -> NameResolver:
    """Create and return a NameResolver instance.

    Args:
        memory_manager: The memory manager to use for reading memory.
        data_mapping_filename: Optional path to a custom data mapping file.

    Returns:
        A NameResolver instance.
    """
    return ConcreteNameResolver(memory_manager, data_mapping_filename)
