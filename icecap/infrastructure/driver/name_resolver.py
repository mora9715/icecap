from icecap.infrastructure.memory_manager import MemoryManager
from functools import lru_cache
from icecap.domain.models import Entity
from icecap.domain.enums import EntityType

from .offsets import (
    UNIT_NAMEBLOCK_OFFSET,
    UNIT_NAMEBLOCK_NAME_OFFSET,
    NAME_MASK_OFFSET,
    NAME_NODE_NAME_OFFSET,
    NAME_STORE_BASE,
    NAME_TABLE_ADDRESS_OFFSET,
)


class NameResolver:
    """
    The class resolves names for game entities.
    """

    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager

    def resolve_name(self, entity: Entity) -> str:
        """
        Resolves the name of the entity based on its type.
        """
        if entity.entity_type == EntityType.UNIT:
            return self._resolve_unit_name(entity)
        elif entity.entity_type == EntityType.PLAYER:
            return self._resolve_player_name(entity)
        raise NotImplementedError(
            f"Name resolution for {entity.entity_type} is not implemented."
        )

    def _resolve_unit_name(self, entity: Entity) -> str:
        try:
            nameblock_address = self.memory_manager.read_uint(
                entity.object_address + UNIT_NAMEBLOCK_OFFSET
            )
            if nameblock_address == 0:
                return "Unknown Unit"
            name_address = self.memory_manager.read_uint(
                nameblock_address + UNIT_NAMEBLOCK_NAME_OFFSET
            )
            if name_address == 0:
                return "Unknown Unit"
            return self.memory_manager.read_string(name_address, length=80)
        except Exception:
            return "Unknown Unit"

    @lru_cache(maxsize=128)
    def _resolve_player_name(self, entity: Entity, max_name_reads: int = 50) -> str:
        mask_address = NAME_STORE_BASE + NAME_MASK_OFFSET
        name_table_address = NAME_STORE_BASE + NAME_TABLE_ADDRESS_OFFSET

        try:
            mask = self.memory_manager.read_uint(mask_address)
            name_base_address = self.memory_manager.read_uint(name_table_address)
        except Exception:
            return "Unknown Player"

        if mask == 0 or name_base_address == 0:
            return "Unknown Player"

        short_guid = entity.guid & 0xFFFFFFFF
        index = mask & short_guid
        bucket_offset = 12 * index

        current_node_address = self.memory_manager.read_uint(
            name_base_address + bucket_offset + 8
        )
        next_node_offset = self.memory_manager.read_uint(
            name_base_address + bucket_offset
        )

        checks = 0
        while current_node_address != 0 and checks < max_name_reads:
            if (current_node_address & 0x1) == 0x1:
                return "Unknown Player"

            node_guid = self.memory_manager.read_uint(current_node_address)
            if node_guid == short_guid:
                name_address = current_node_address + NAME_NODE_NAME_OFFSET
                return self.memory_manager.read_string(name_address, length=40)

            # Step to next node
            try:
                next_node_address = current_node_address + next_node_offset + 4
                current_node_address = self.memory_manager.read_uint(next_node_address)
            except Exception:
                break

            checks += 1

        return "Unknown Player"
